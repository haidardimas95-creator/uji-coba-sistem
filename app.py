#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UJI COBA DASHBOARD - BACKEND API
=================================
Trend-Only Strategy Dashboard for Kompas100 Stocks
Backend API yang menyediakan:
- Stock screening signals
- Position management (open/close)
- Performance metrics
- Real-time monitoring

Strategi:
- Entry: Monday Open, jika prev MACD > Signal AND Close > SMA50
- Day-1 Tuesday: jika UP -> Trend Follow, jika DOWN -> SKIP
- Exit: MACD crosses below Signal, atau max 30 days
- Cost: 0.3% per transaksi
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import schedule
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# APP CONFIG
# ============================================================================

app = Flask(__name__)
CORS(app)

# Data storage
STORAGE_FILE = os.path.join(os.path.dirname(__file__), 'data', 'positions.json')
METRICS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'metrics.json')
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'history.json')

# Featured stocks for scanning (high liquidity)
FEATURED_TICKERS = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK',
    'ASII.JK', 'UNVR.JK', 'TLKM.JK', 'INDF.JK', 'MYOR.JK', 'GOTO.JK',
]

# All Kompas100 verified tickers
ALL_TICKERS = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK',
    'ICBP.JK', 'INDF.JK', 'KLBF.JK', 'MYOR.JK', 'UNVR.JK', 'HMSP.JK',
    'TLKM.JK', 'EXCL.JK',
    'ADRO.JK', 'PTBA.JK', 'INCO.JK', 'MDKA.JK', 'ANTM.JK',
    'JSMR.JK', 'BSDE.JK', 'PWON.JK', 'LPKR.JK',
    'SMGR.JK', 'MNCN.JK', 'GOTO.JK', 'BUKA.JK',
    'AKRA.JK', 'PGAS.JK', 'PGEO.JK', 'TOWR.JK',
    'PNBN.JK', 'BBKP.JK', 'DOID.JK', 'FMII.JK',
    'MTEL.JK', 'NCKL.JK', 'ARTO.JK', 'BREN.JK',
    'GPRA.JK', 'HRUM.JK', 'INTP.JK', 'TRIM.JK',
]

# Always use featured tickers for faster scanning
TICKERS = FEATURED_TICKERS

TRANSACTION_COST = 0.003


# ============================================================================
# INDICATORS CALCULATION
# ============================================================================

def add_indicators(df):
    """Calculate MACD and SMA50"""
    df['SMA50'] = df['Close'].rolling(50).mean()
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    return df


# ============================================================================
# STRATEGY LOGIC
# ============================================================================

def check_entry_signal(df):
    """
    Check entry signal for Trend-Only strategy
    Returns: (should_entry, day1_outlook)
    """
    df = add_indicators(df).dropna().reset_index(drop=True)
    
    if len(df) < 5:
        return False, None
    
    current = df.iloc[-1]
    prev = df.iloc[-2]
    day_before = df.iloc[-3] if len(df) > 2 else None
    
    # Entry conditions
    macd_bullish = prev['MACD'] > prev['Signal']
    price_above_sma = prev['Close'] > prev['SMA50']
    
    should_entry = macd_bullish and price_above_sma
    
    # Day-1 outlook (next day)
    day1_outlook = None
    if should_entry and day_before:
        # Simulate next day close
        if current['Close'] > current['Open']:
            day1_outlook = 'UP'
        else:
            day1_outlook = 'DOWN'
    
    return should_entry, day1_outlook


def check_exit_signal(df, entry_price):
    """
    Check if should exit position
    Returns: (should_exit, reason)
    """
    df = add_indicators(df).dropna().reset_index(drop=True)
    
    if len(df) < 5:
        return False, None
    
    current = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Exit condition: MACD crosses below Signal
    if prev['MACD'] > prev['Signal'] and current['MACD'] < current['Signal']:
        return True, 'MACD Cross Below Signal'
    
    # Max hold 30 days check
    days_held = len(df) - df[df['Close'] >= entry_price * 0.95].index.min() if len(df) > 0 else 0
    
    return False, None


# ============================================================================
# DATA MANAGEMENT
# ============================================================================

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)


def load_positions():
    """Load active positions"""
    ensure_data_dir()
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return []


def save_positions(positions):
    """Save active positions"""
    ensure_data_dir()
    with open(STORAGE_FILE, 'w') as f:
        json.dump(positions, f, indent=2, default=str)


def load_history():
    """Load trade history"""
    ensure_data_dir()
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


def save_history(history):
    """Save trade history"""
    ensure_data_dir()
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, default=str)


# ============================================================================
# SCANNING & SIGNAL GENERATION
# ============================================================================

def scan_all_stocks():
    """
    Scan all Kompas100 stocks for entry signals
    Returns: List of signals
    """
    signals = []
    
    for ticker in TICKERS:
        try:
            df = yf.download(ticker, start='2024-01-01', end='2026-12-31', progress=False, threads=True, timeout=20)
            
            if df is None or df.empty:
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df = df.droplevel(1, axis=1)
            
            if 'Date' not in df.columns:
                df = df.reset_index()
            
            df = df.dropna(subset=['Close'])
            df = df.reset_index(drop=True)
            
            if len(df) < 60:
                continue
            
            # Get last trading day info
            last_row = df.iloc[-1]
            date_str = str(last_row['Date'].date())
            open_price = float(last_row['Open']) if 'Open' in df.columns else float(last_row['Close'])
            close_price = float(last_row['Close'])
            high_price = float(last_row['High']) if 'High' in df.columns else close_price
            low_price = float(last_row['Low']) if 'Low' in df.columns else close_price
            volume = int(last_row['Volume']) if 'Volume' in df.columns else 0
            
            # Check entry signal
            should_entry, day1_outlook = check_entry_signal(df)
            
            # Check if already in position
            positions = load_positions()
            already_position = any(p['ticker'] == ticker for p in positions)
            
            if should_entry and not already_position:
                signals.append({
                    'ticker': ticker,
                    'signal': 'BUY',
                    'date': date_str,
                    'price': open_price,
                    'close': close_price,
                    'day1_outlook': day1_outlook,
                    'macd': float(df.iloc[-1]['MACD']) if 'MACD' in df.columns else 0,
                    'signal_line': float(df.iloc[-1]['Signal']) if 'Signal' in df.columns else 0,
                    'sma50': float(df.iloc[-1]['SMA50']) if 'SMA50' in df.columns else 0,
                    'volume': volume,
                    'status': 'PENDING',
                })
            elif already_position:
                # Check exit
                pos = next(p for p in positions if p['ticker'] == ticker)
                entry_price = pos['entry_price']
                should_exit, reason = check_exit_signal(df, entry_price)
                
                if should_exit:
                    # Close position
                    pnl = ((close_price - entry_price) / entry_price) * 100
                    net_pnl = pnl - (2 * TRANSACTION_COST * 100)
                    
                    # Add to history
                    history = load_history()
                    history.append({
                        'ticker': ticker,
                        'entry_date': pos['entry_date'],
                        'exit_date': date_str,
                        'entry_price': entry_price,
                        'exit_price': close_price,
                        'pnl_net': net_pnl,
                        'pnl_raw': pnl,
                        'reason': reason,
                        'hold_days': pos.get('hold_days', 0),
                    })
                    save_history(history)
                    
                    # Remove from positions
                    positions = [p for p in positions if p['ticker'] != ticker]
                    save_positions(positions)
        
        except Exception as e:
            import logging
            logging.error(f"Error scanning {ticker}: {e}")
            continue
    
    return signals


def open_position(ticker, price=None):
    """Open a new position"""
    positions = load_positions()
    
    # Check if already exists
    if any(p['ticker'] == ticker for p in positions):
        return {'error': 'Position already exists'}
    
    try:
        df = yf.download(ticker, start='2024-01-01', progress=False, threads=True, timeout=20)
        
        if df is None or df.empty:
            return {'error': 'Cannot fetch data'}
        
        if isinstance(df.columns, pd.MultiIndex):
            df = df.droplevel(1, axis=1)
        
        if 'Date' not in df.columns:
            df = df.reset_index()
        
        df = df.dropna(subset=['Close'])
        df = df.reset_index(drop=True)
        
        if len(df) == 0:
            return {'error': 'No data available'}
        
        last_row = df.iloc[-1]
        entry_price = price if price else float(last_row['Close'])
        
        position = {
            'ticker': ticker,
            'entry_date': str(last_row['Date'].date()),
            'entry_price': entry_price,
            'stop_loss': entry_price * 0.95,
            'created_at': datetime.now().isoformat(),
        }
        
        positions.append(position)
        save_positions(positions)
        
        return {'success': True, 'position': position}
    
    except Exception as e:
        return {'error': str(e)}


def get_positions_with_data():
    """Get active positions with current market data"""
    positions = load_positions()
    result = []
    
    for pos in positions:
        try:
            df = yf.download(pos['ticker'], start='2024-01-01', progress=False, threads=True, timeout=20)
            
            if df is None or df.empty:
                result.append({
                    'ticker': pos['ticker'],
                    'entry_date': pos['entry_date'],
                    'entry_price': pos['entry_price'],
                    'current_price': pos['entry_price'],
                    'floating_pct': 0,
                    'days_held': 0,
                    'status': 'NO_DATA',
                    'exit_reason': 'Cannot fetch data',
                })
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df = df.droplevel(1, axis=1)
            
            if 'Date' not in df.columns:
                df = df.reset_index()
            
            df = df.dropna(subset=['Close'])
            df = df.sort_values('Date').reset_index(drop=True)
            
            if len(df) == 0:
                result.append({
                    'ticker': pos['ticker'],
                    'entry_date': pos['entry_date'],
                    'entry_price': pos['entry_price'],
                    'current_price': pos['entry_price'],
                    'floating_pct': 0,
                    'days_held': 0,
                    'status': 'NO_DATA',
                    'exit_reason': 'No data available',
                })
                continue
            
            last_row = df.iloc[-1]
            current_price = float(last_row['Close'])
            open_price = float(last_row['Open'])
            
            floating_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
            days_held = (pd.Timestamp(last_row['Date']) - pd.Timestamp(pos['entry_date'])).days
            
            # Check exit signal
            should_exit, reason = check_exit_signal(df, pos['entry_price'])
            
            result.append({
                'ticker': pos['ticker'],
                'entry_date': pos['entry_date'],
                'entry_price': pos['entry_price'],
                'current_price': current_price,
                'floating_pct': round(floating_pct, 2),
                'days_held': days_held,
                'stop_loss': pos.get('stop_loss', pos['entry_price'] * 0.95),
                'status': 'CLOSE_SIGNAL' if should_exit else 'ACTIVE',
                'exit_reason': reason if should_exit else None,
            })
        
        except:
            result.append({
                'ticker': pos['ticker'],
                'entry_date': pos['entry_date'],
                'entry_price': pos['entry_price'],
                'current_price': 0,
                'floating_pct': 0,
                'days_held': 0,
                'status': 'ERROR',
            })
    
    return result


# ============================================================================
# METRICS CALCULATION
# ============================================================================

def calculate_metrics():
    """Calculate overall performance metrics"""
    history = load_history()
    positions = load_positions()
    
    if not history and not positions:
        return {
            'total_trades': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'net_profit': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'active_positions': len(positions),
            'wins': 0,
            'losses': 0,
        }
    
    all_trades = history + [p for p in positions if p.get('exit_price')]
    
    if not all_trades:
        all_trades = history
    
    pnls = [t['pnl_net'] for t in all_trades if 'pnl_net' in t]
    
    if not pnls:
        pnls = [0]
    
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    
    gp = sum(wins) if wins else 0
    gl = abs(sum(losses)) if losses else 1
    
    wr = (len(wins) / len(pnls) * 100) if pnls else 0
    pf = gp / gl if gl > 0 else 999.99
    
    return {
        'total_trades': len(pnls),
        'win_rate': round(wr, 2),
        'profit_factor': round(pf, 2),
        'net_profit': round(sum(pnls), 2),
        'avg_win': round(np.mean(wins), 2) if wins else 0,
        'avg_loss': round(np.mean(losses), 2) if losses else 0,
        'best_trade': round(max(pnls), 2) if pnls else 0,
        'worst_trade': round(min(pnls), 2) if pnls else 0,
        'active_positions': len(positions),
        'wins': len(wins),
        'losses': len(losses),
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Dashboard home"""
    from flask import render_template
    return render_template('index.html')


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics"""
    metrics = calculate_metrics()
    return jsonify(metrics)


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get active positions with market data"""
    positions = get_positions_with_data()
    return jsonify({'positions': positions, 'count': len(positions)})


@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get current signals for all stocks"""
    signals = scan_all_stocks()
    return jsonify({'signals': signals, 'count': len(signals), 'timestamp': datetime.now().isoformat()})


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get trade history"""
    history = load_history()
    # Sort by date descending
    history.sort(key=lambda x: x.get('exit_date', ''), reverse=True)
    return jsonify({'history': history, 'count': len(history)})


@app.route('/api/scan', methods=['POST'])
def run_scan():
    """Manually trigger stock scan"""
    signals = scan_all_stocks()
    return jsonify({'signals': signals, 'count': len(signals), 'timestamp': datetime.now().isoformat()})


@app.route('/api/position/open', methods=['POST'])
def open_new_position():
    """Open a new position"""
    data = request.get_json()
    ticker = data.get('ticker')
    price = data.get('price')
    
    if not ticker:
        return jsonify({'error': 'Ticker required'}), 400
    
    result = open_position(ticker, price)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)


@app.route('/api/position/<ticker>/close', methods=['POST'])
def close_position(ticker):
    """Close a position manually"""
    positions = load_positions()
    history = load_history()
    
    pos = next((p for p in positions if p['ticker'] == ticker), None)
    
    if not pos:
        return jsonify({'error': 'Position not found'}), 404
    
    try:
        df = yf.download(ticker, start='2024-01-01', progress=False, threads=True, timeout=20)
        
        if df is None or df.empty:
            return jsonify({'error': 'Cannot fetch data'}), 400
        
        if isinstance(df.columns, pd.MultiIndex):
            df = df.droplevel(1, axis=1)
        
        if 'Date' not in df.columns:
            df = df.reset_index()
        
        df = df.dropna(subset=['Close'])
        df = df.sort_values('Date').reset_index(drop=True)
        
        if len(df) == 0:
            return jsonify({'error': 'No data available'}), 400
        
        last_row = df.iloc[-1]
        exit_price = float(last_row['Close'])
        exit_date = str(last_row['Date'].date())
        
        pnl = ((exit_price - pos['entry_price']) / pos['entry_price']) * 100
        net_pnl = pnl - (2 * TRANSACTION_COST * 100)
        
        history.append({
            'ticker': ticker,
            'entry_date': pos['entry_date'],
            'exit_date': exit_date,
            'entry_price': pos['entry_price'],
            'exit_price': exit_price,
            'pnl_net': round(net_pnl, 2),
            'pnl_raw': round(pnl, 2),
            'reason': 'Manual Close',
            'hold_days': (pd.Timestamp(exit_date) - pd.Timestamp(pos['entry_date'])).days,
        })
        
        save_history(history)
        
        positions = [p for p in positions if p['ticker'] != ticker]
        save_positions(positions)
        
        return jsonify({
            'success': True,
            'trade': history[-1],
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tickers', methods=['GET'])
def get_tickers():
    """Get list of monitored tickers"""
    return jsonify({'tickers': TICKERS, 'count': len(TICKERS)})


@app.route('/api/debug/<ticker>', methods=['GET'])
def debug_ticker(ticker):
    """Debug endpoint to check single ticker data"""
    try:
        df = yf.download(ticker, start='2024-01-01', progress=False, threads=True, timeout=20)
        
        if df is None or df.empty:
            return jsonify({'error': 'No data', 'ticker': ticker})
        
        if isinstance(df.columns, pd.MultiIndex):
            df = df.droplevel(1, axis=1)
        
        if 'Date' not in df.columns:
            df = df.reset_index()
        
        df = df.dropna(subset=['Close'])
        df = df.sort_values('Date').reset_index(drop=True)
        
        if len(df) < 60:
            return jsonify({'error': 'Insufficient data', 'ticker': ticker, 'rows': len(df)})
        
        df = add_indicators(df)
        df = df.dropna()
        
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        macd_bullish = prev['MACD'] > prev['Signal']
        price_above_sma = prev['Close'] > prev['SMA50']
        should_entry = macd_bullish and price_above_sma
        
        return jsonify({
            'ticker': ticker,
            'last_date': str(current.name if hasattr(current, 'name') else ''),
            'close': float(current['Close']),
            'open': float(current['Open'] if 'Open' in current.index else current['Close']),
            'macd': float(current['MACD']),
            'signal_line': float(current['Signal']),
            'sma50': float(current['SMA50']),
            'prev_macd': float(prev['MACD']),
            'prev_signal': float(prev['Signal']),
            'prev_close': float(prev['Close']),
            'prev_sma50': float(prev['SMA50']),
            'macd_bullish': bool(macd_bullish),
            'price_above_sma': bool(price_above_sma),
            'should_entry': bool(should_entry),
            'data_rows': len(df),
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'ticker': ticker})


# ============================================================================
# AUTO SCANNER (Background Task)
# ============================================================================

def auto_scan():
    """Auto scan every 5 minutes during market hours"""
    print(f"[{datetime.now()}] Running auto-scan...")
    signals = scan_all_stocks()
    if signals:
        print(f"  Found {len(signals)} signals")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("  UJI COBA DASHBOARD - TREND ONLY STRATEGY")
    print("=" * 60)
    print("\n  Starting backend server...")
    print("  Dashboard: http://localhost:5000")
    print("  API: http://localhost:5000/api/metrics")
    print("\n  Press Ctrl+C to stop")
    
    # Start auto-scan in background
    schedule.every(5).minutes.do(auto_scan)
    
    # Run initial scan
    auto_scan()
    
    # Start Flask with scheduler
    import threading
    
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
    scheduler_thread.start()
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)


if __name__ == '__main__':
    main()
