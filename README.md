# UJI COBA DASHBOARD - Trend-Only Strategy

Dashboard monitoring untuk strategi Trend-Only pada saham Kompas100.

## Fitur

- **Stock Screening**: Deteksi sinyal entry berdasarkan MACD + SMA50
- **Position Management**: Buka dan tutup posisi secara manual
- **Performance Metrics**: Win Rate, Profit Factor, Average Win/Loss, dll
- **Real-time Monitoring**: Auto-refresh setiap 30 detik
- **Performance Map**: Visualisasi performa posisi aktif

## Strategi Trend-Only

### Entry Condition
- Hari: Senin
- MACD(12,26,9) > Signal Line(9)
- Close Price > SMA(50)

### Exit Condition
- Day-1 (Selasa) UP: Hold sampai MACD crosses below Signal atau max 30 hari
- Day-1 (Selasa) DOWN: SKIP (tidak entry)

### Transaction Cost
- 0.3% per transaksi (0.6% round trip)

## Instalasi

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Dashboard

```bash
python app.py
```

### 3. Buka Browser

Akses dashboard di: http://localhost:5000

## Struktur File

```
ujicoba-dashboard/
├── app.py                    # Backend Flask API
├── requirements.txt          # Python dependencies
├── README.md                 # Dokumentasi ini
├── data/                     # Data storage (auto-created)
│   ├── positions.json        # Active positions
│   ├── metrics.json          # Performance metrics
│   └── history.json          # Trade history
├── templates/
│   └── index.html           # Frontend dashboard
└── static/
    ├── css/
    │   └── style.css        # Dashboard styling
    └── js/
        └── dashboard.js     # Frontend logic
```

## API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/metrics` | GET | Get performance metrics |
| `/api/positions` | GET | Get active positions |
| `/api/signals` | GET | Get current signals |
| `/api/history` | GET | Get trade history |
| `/api/scan` | POST | Manually trigger scan |
| `/api/position/open` | POST | Open new position |
| `/api/position/<ticker>/close` | POST | Close position |
| `/api/tickers` | GET | Get list of tickers |

## Deployment

### Deploy ke Railway.app (Gratis - Recommended)

Lihat [`RAILWAY_DEPLOY.md`](RAILWAY_DEPLOY.md) untuk panduan lengkap.

**Singkat:**
1. Upload kode ke GitHub
2. Login ke Railway.app → New Project → Deploy from GitHub
3. Railway otomatis deploy → dapat URL gratis

### Option 2: Heroku

1. Buat file `Procfile`:
```
web: gunicorn app:app
```

2. Deploy ke Heroku:
```bash
heroku create your-app-name
git push heroku main
heroku ps:scale web=1
```

### Option 2: VPS/Linux

1. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

2. Setup virtual environment:
```bash
cd ujicoba-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run with gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

4. Setup systemd service:
```bash
sudo nano /etc/systemd/system/ujicoba.service
```

```ini
[Unit]
Description=Uji Coba Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/ujicoba-dashboard
Environment="PATH=/path/to/ujicoba-dashboard/venv/bin"
ExecStart=/path/to/ujicoba-dashboard/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

5. Start service:
```bash
sudo systemctl enable ujicoba
sudo systemctl start ujicoba
sudo systemctl status ujicoba
```

### Option 3: Docker

1. Buat file `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

2. Build dan run:
```bash
docker build -t ujicoba-dashboard .
docker run -p 5000:5000 ujicoba-dashboard
```

## Konfigurasi

Edit file `app.py` untuk mengubah:
- `TICKERS`: Daftar saham yang dimonitor
- `TRANSACTION_COST`: Biaya transaksi
- `OOS_START`/`OOS_END`: Periode backtest

## Troubleshooting

### Error: Module not found
```bash
pip install -r requirements.txt
```

### Error: Port already in use
```bash
# Change port in app.py
app.run(host='0.0.0.0', port=5001)
```

### Error: Cannot fetch data
- Pastikan koneksi internet aktif
- Yahoo Finance API mungkin rate-limited

## License

MIT License
