================================================================================
PANDUAN DEPLOY MANUAL - UJICOBA DASHBOARD
Tanpa Git, Tanpa Command Line
Hanya butuh Browser!
================================================================================

================================================================================
LANGKAH 1: BUA T REPOSITORY DI GITHUB
================================================================================

1. Buka browser, kunjungi: https://github.com/new

2. Login dengan account: haidardimas95

3. Isi form:
   - Repository name: ujicoba-dashboard
   - Description: Trend-Only Trading Dashboard (Optional)
   - Visibility: Pilih PUBLIC
   - TIDAK centang "Add a README file"
   - TIDAK centang "Add .gitignore"
   - TIDAK centang "Add a license"

4. Klik tombol hijau "Create repository"

5. Setelah halaman reload, Anda akan melihat halaman repo kosong


================================================================================
LANGKAH 2: UPLOAD KODE KE GITHUB
================================================================================

1. Di halaman repository yang baru dibuat, cari teks kecil:
   "\"uploading an existing file\""
   atau klik link "uploading an existing file"

2. Akan muncul area drag & drop file

3. Buka File Explorer Windows, navigasi ke:
   C:\Users\Aldi Firmansyah\Desktop\ujicoba-dashboard\

4. DRAG & DROP semua file dan folder berikut ke browser:

   FILE (drag satu per satu atau sekaligus):
   ─────────────────────────────────────────
   ✓ app.py
   ✓ requirements.txt
   ✓ Procfile
   ✓ Dockerfile
   ✓ railway.json
   ✓ .gitignore
   ✓ README.md

   FOLDER (drag seluruh folder):
   ─────────────────────────────────────────
   ✓ FOLDER templates/ (akan include index.html)
   ✓ FOLDER static/ (akan include css/style.css dan js/dashboard.js)

5. Setelah semua file ter-upload, akan muncul di halaman upload

6. Isi "Commit changes":
   - Commit message: "Initial commit - ujicoba-dashboard"

7. Klik tombol hijau "Commit changes" atau "Upload files"

8. Tunggu sampai selesai

9. VERIFIKASI: Anda harus melihat semua file di repository:
   └── ujicoba-dashboard/
       ├── app.py
       ├── requirements.txt
       ├── Procfile
       ├── Dockerfile
       ├── railway.json
       ├── .gitignore
       ├── README.md
       ├── templates/
       │   └── index.html
       └── static/
           ├── css/
           │   └── style.css
           └── js/
               └── dashboard.js


================================================================================
LANGKAH 3: DEPLOY KE RAILWAY.APP
================================================================================

1. Buka browser baru, kunjungi: https://railway.app

2. Login dengan GitHub:
   - Klik "Login" atau "Sign Up"
   - Pilih "Login with GitHub"
   - Authorize Railway untuk akses GitHub

3. Di Dashboard Railway, klik "New Project"

4. Pilih "Private Repo" atau "Public Repo" (tergantung setting GitHub Anda)

5. Cari dan pilih repository: ujicoba-dashboard

6. Railway akan auto-detect configuration dari:
   - Procfile ATAU
   - Dockerfile ATAU
   - railway.json

7. Jika diminta environment variables:
   - Tidak perlu tambah apa-apa (app menggunakan yfinance tanpa API key)
   - Klik "Deploy"

8. Tunggu 2-5 menit sampai build selesai

9. Dashboard akan live di URL:
   https://ujicoba-dashboard-xxxxx.up.railway.app

10. Buka URL tersebut di browser atau tab baru


================================================================================
TROUBLESHOOTING
================================================================================

MASALAH: File tidak ter-upload semuanya
SOLUSI: Pastikan folder templates/ dan static/ terdrag sebagai folder,
        bukan dibuka dulu

MASALAH: Build di Railway gagal
SOLUSI: Cek log di Railway dashboard, pastikan:
        - requirements.txt ada di root repository
        - Procfile atau Dockerfile ada
        - app.py ada di root repository

MASALAH: Dashboard tidak bisa load data
SOLUSI: yfinance mungkin slow/blocked. Tunggu beberapa detik
        atau coba refresh halaman

MASALAH: Port sudah terpakai di Railway
SOLUSI: Railway otomatis set PORT environment variable.
        Kode sudah handle ini dengan ${PORT:-5000}


================================================================================
SELESAI!
================================================================================

Dashboard Anda sudah live dan bisa diakses dari mana saja!

URL Dashboard: https://ujicoba-dashboard-xxxxx.up.railway.app

================================================================================
