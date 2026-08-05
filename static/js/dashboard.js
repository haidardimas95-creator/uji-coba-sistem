// === CONFIG ===
const API_BASE = `${window.location.origin}/api`;

// === DOM READY ===
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadMetrics();
    loadPositions();
    loadHistory();
    loadSignals();
    
    // Auto refresh every 30 seconds
    setInterval(() => {
        loadMetrics();
        loadPositions();
    }, 30000);
});

// === TABS ===
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active from all tabs
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active to clicked tab
            tab.classList.add('active');
            const tabId = tab.dataset.tab;
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.dataset.filter;
            filterPositions(filter);
        });
    });
}

// === LOAD METRICS ===
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`, { signal: AbortSignal.timeout(15000) });
        const metrics = await response.json();
        
        document.getElementById('win-rate').textContent = `${metrics.win_rate}%`;
        document.getElementById('profit-factor').textContent = metrics.profit_factor.toFixed(2);
        document.getElementById('avg-win').textContent = `+${metrics.avg_win}%`;
        document.getElementById('avg-loss').textContent = `${metrics.avg_loss}%`;
        document.getElementById('net-profit').textContent = `${metrics.net_profit > 0 ? '+' : ''}${metrics.net_profit}%`;
        document.getElementById('active-positions').textContent = metrics.active_positions;
        
        // Color coding
        const netProfitEl = document.getElementById('net-profit');
        netProfitEl.style.color = metrics.net_profit >= 0 ? 'var(--green)' : 'var(--red)';
        
        updateTimestamp();
    } catch (error) {
        console.error('Error loading metrics:', error);
        document.getElementById('win-rate').textContent = 'N/A';
        document.getElementById('profit-factor').textContent = 'N/A';
    }
}

// === LOAD POSITIONS ===
async function loadPositions() {
    try {
        const response = await fetch(`${API_BASE}/positions`, { signal: AbortSignal.timeout(30000) });
        const data = await response.json();
        
        const tbody = document.getElementById('positions-table');
        if (data.positions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="loading">Tidak ada posisi aktif</td></tr>';
            updatePerformanceMap([]);
            return;
        }
        
        tbody.innerHTML = data.positions.map(pos => {
            const floatClass = pos.floating_pct > 0 ? 'float-positive' : (pos.floating_pct < 0 ? 'float-negative' : 'float-zero');
            const floatSign = pos.floating_pct > 0 ? '+' : '';
            const statusClass = pos.status === 'CLOSE_SIGNAL' ? 'status-close-signal' : 'status-active';
            const statusText = pos.status === 'CLOSE_SIGNAL' ? 'EXIT SIGNAL' : 'POSISI AKTIF';
            
            return `
                <tr>
                    <td><strong>${pos.ticker}</strong></td>
                    <td><span class="signal-buy"><i class="fas fa-arrow-up"></i> BUY</span></td>
                    <td>${pos.entry_date}</td>
                    <td>${formatPrice(pos.entry_price)}</td>
                    <td>${formatPrice(pos.current_price)}</td>
                    <td class="${floatClass}">${floatSign}${pos.floating_pct}%</td>
                    <td><span class="${statusClass}">${statusText}</span></td>
                    <td>
                        <button class="btn-close-pos" onclick="closePosition('${pos.ticker}')">
                            <i class="fas fa-times"></i> Close
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
        
        updatePerformanceMap(data.positions);
    } catch (error) {
        console.error('Error loading positions:', error);
        document.getElementById('positions-table').innerHTML = '<tr><td colspan="8" class="loading">Gagal memuat data posisi. Coba klik "Refresh".</td></tr>';
    }
}

// === LOAD HISTORY ===
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history`, { signal: AbortSignal.timeout(10000) });
        const data = await response.json();
        
        const tbody = document.getElementById('history-table');
        if (data.history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Belum ada riwayat trade</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.history.slice(0, 20).map(trade => {
            const resultClass = trade.pnl_net > 0 ? 'float-positive' : 'float-negative';
            const resultSign = trade.pnl_net > 0 ? '+' : '';
            
            return `
                <tr>
                    <td><strong>${trade.ticker}</strong></td>
                    <td>${trade.entry_date}</td>
                    <td>${formatPrice(trade.entry_price)}</td>
                    <td>${trade.exit_date}</td>
                    <td>${formatPrice(trade.exit_price)}</td>
                    <td class="${resultClass}">${resultSign}${trade.pnl_net.toFixed(2)}%</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// === LOAD SIGNALS (PENDING) ===
async function loadSignals() {
    try {
        console.log('Loading signals...');
        const response = await fetch(`${API_BASE}/signals`, { signal: AbortSignal.timeout(60000) });
        const data = await response.json();
        console.log('Signals loaded:', data);
        
        const tbody = document.getElementById('pending-table');
        if (data.signals.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">Tidak ada sinyal saat ini</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.signals.map(signal => {
            const day1Class = signal.day1_outlook === 'UP' ? 'float-positive' : 'float-negative';
            const day1Text = signal.day1_outlook === 'UP' ? 'UP ▲' : 'DOWN ▼';
            
            return `
                <tr>
                    <td><strong>${signal.ticker}</strong></td>
                    <td><span class="signal-buy">BUY</span></td>
                    <td>${formatPrice(signal.price)}</td>
                    <td class="${day1Class}">${day1Text}</td>
                    <td>${signal.macd.toFixed(4)}</td>
                    <td>${signal.signal_line.toFixed(4)}</td>
                    <td><span class="status-pending">PENDING - BUKA BESOK</span></td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading signals:', error);
        document.getElementById('pending-table').innerHTML = '<tr><td colspan="7" class="loading">Gagal memuat sinyal. API mungkin sedang loading atau timeout. Coba klik "Refresh".</td></tr>';
    }
}

// === UPDATE PERFORMANCE MAP ===
function updatePerformanceMap(positions) {
    const grid = document.getElementById('performance-grid');
    
    if (positions.length === 0) {
        grid.innerHTML = '<p style="color: var(--text-secondary);">Tidak ada posisi aktif</p>';
        return;
    }
    
    grid.innerHTML = positions.map(pos => {
        const cls = pos.floating_pct > 0 ? 'positive' : (pos.floating_pct < 0 ? 'negative' : 'neutral');
        const sign = pos.floating_pct > 0 ? '+' : '';
        
        return `
            <div class="perf-item ${cls}">
                <div class="ticker-name">${pos.ticker}</div>
                <div class="perf-value">${sign}${pos.floating_pct}%</div>
            </div>
        `;
    }).join('');
}

// === FILTER POSITIONS ===
function filterPositions(filter) {
    const rows = document.querySelectorAll('#positions-table tr');
    
    rows.forEach(row => {
        if (filter === 'all') {
            row.style.display = '';
            return;
        }
        
        if (filter === 'active') {
            const status = row.querySelector('.status-active');
            row.style.display = status ? '' : 'none';
        }
        
        if (filter === 'pending') {
            const status = row.querySelector('.status-pending');
            row.style.display = status ? '' : 'none';
        }
    });
}

// === CLOSE POSITION ===
async function closePosition(ticker) {
    if (!confirm(`Close position ${ticker}?`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/position/${ticker}/close`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Position ${ticker} closed successfully!`);
            loadPositions();
            loadHistory();
            loadMetrics();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Error closing position: ' + error.message);
    }
}

// === REFRESH ALL DATA ===
async function refreshData() {
    const btn = document.querySelector('.btn-scan');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    
    await Promise.all([
        loadMetrics(),
        loadPositions(),
        loadHistory(),
        loadSignals(),
    ]);
    
    btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
}

// === FORMAT PRICE ===
function formatPrice(price) {
    if (!price || price === 0) return '-';
    return price.toLocaleString('id-ID', { minimumFractionDigits: 0, maximumFractionDigits: 3 });
}

// === UPDATE TIMESTAMP ===
function updateTimestamp() {
    const now = new Date();
    const timeStr = now.toLocaleString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
    document.getElementById('last-update').textContent = `Last update: ${timeStr}`;
}
