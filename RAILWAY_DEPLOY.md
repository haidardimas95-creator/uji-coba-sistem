# Panduan Deploy ke Railway.app (Gratis)

## Langkah 1: Persiapan

### 1.1 Pastikan sudah punya:
- Akun GitHub
- Akun Railway.app (https://railway.app)

### 1.2 Upload kode ke GitHub

```bash
# Buat repository baru di GitHub
git init
git add .
git commit -m "Initial commit - Uji Coba Dashboard"
git branch -M main
git remote add origin https://githubUSERNAME/ujicoba-dashboard.git
git push -u origin main
```

## Langkah 2: Deploy ke Railway

### 2.1 Login ke Railway
1. Buka https://railway.app
2. Klik "Login" → Pilih "Sign in with GitHub"

### 2.2 Create Project
1. Klik "New Project"
2. Pilih "Deploy from GitHub repo"
3. Pilih repository `ujicoba-dashboard` yang sudah dibuat

### 2.3 Konfigurasi
Railway akan otomatis detect Flask app. Jika tidak:

1. Masuk ke project → Go to Settings → Build Strategy
2. Set "Build Command": `pip install -r requirements.txt`
3. Set "Start Command": `gunicorn app:app`

### 2.4 Deploy
1. Klik "Deploy New Version"
2. Tunggu proses build selesai (2-5 menit)
3. Railway akan memberikan URL: `https://ujicoba-dashboard-xxxx.up.railway.app`

## Langkah 3: Konfigurasi Environment (Optional)

Jika perlu environment variables:
1. Masuk ke project → Variables tab
2. Tambahkan variable jika perlu

## Langkah 4: Akses Dashboard

Buka URL yang diberikan Railway:
```
https://ujicoba-dashboard-xxxx.up.railway.app
```

## Troubleshooting

### Error: Build Failed
- Pastikan `requirements.txt` ada di root folder
- Cek log build di Railway dashboard

### Error: Process Failed to Start
- Pastikan `gunicorn` ada di requirements.txt
- Cek start command: `gunicorn app:app`

### Error: Module Not Found
- Pastikan semua dependencies ada di requirements.txt

## Free Tier Limitations

Railway free tier:
- 500 hours/month deployment time
- 512MB RAM
- 1GB Storage
- Auto-sleep setelah 90 menit inactive

## Custom Domain (Optional)

1. Masuk project → Settings → Domains
2. Tambahkan custom domain
3. Update DNS records sesuai instruksi

## Update Aplikasi

Setiap kali push ke GitHub, Railway akan otomatis deploy:
```bash
git add .
git commit -m "Update fitur X"
git push
```
