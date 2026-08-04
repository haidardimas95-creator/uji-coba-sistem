@echo off
chcp 65001 >nul
echo ========================================
echo   Deploy ujicoba-dashboard to Railway
echo ========================================
echo.

REM ============================================
REM CONFIG - UBAH BAGIAN INI
REM ============================================
set GITHUB_TOKEN=YOUR_TOKEN_HERE
set GITHUB_USER=haidardimas95
set REPO_NAME=ujicoba-dashboard
REM ============================================

echo [Step 1] Navigating to project folder...
cd /d "%~dp0ujicoba-dashboard"

echo [Step 2] Initializing Git...
"C:\Program Files\Git\bin\git.exe" init
if errorlevel 1 (
    echo ERROR: Git not found!
    pause
    exit /b 1
)

echo [Step 3] Adding files...
"C:\Program Files\Git\bin\git.exe" add .

echo [Step 4] Creating commit...
"C:\Program Files\Git\bin\git.exe" commit -m "Initial commit - ujicoba-dashboard"

echo [Step 5] Setting remote repository...
"C:\Program Files\Git\bin\git.exe" remote remove origin 2>nul
"C:\Program Files\Git\bin\git.exe" remote add origin https://%GITHUB_TOKEN%@github.com/%GITHUB_USER%/%REPO_NAME%.git

echo [Step 6] Pushing to GitHub...
"C:\Program Files\Git\bin\git.exe" branch -M main
"C:\Program Files\Git\bin\git.exe" push -u origin main

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Please check:
    echo 1. Is your GITHUB_TOKEN correct?
    echo 2. Does repository %GITHUB_USER%/%REPO_NAME% exist on GitHub?
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS! Code pushed to GitHub
echo ========================================
echo.
echo Repository: https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
echo Next: Deploy to Railway.app
echo 1. Buka https://railway.app
echo 2. Klik 'New Project'
echo 3. Pilih 'Import from GitHub'
echo 4. Pilih repo: %GITHUB_USER%/%REPO_NAME%
echo 5. Railway akan auto-detect config
echo.
pause
