# ============================================================================
# GitHub Push Script for ujicoba-dashboard
# ============================================================================
# Instructions:
# 1. Replace $GITHUB_TOKEN with your actual PAT (e.g., "github_pat_11Bxxxx...")
# 2. Replace $GITHUB_USERNAME with your GitHub username (e.g., "haidardimas95")
# 3. Run this script in PowerShell
# ============================================================================

$GITHUB_TOKEN = "YOUR_GITHUB_PAT_HERE"  # Replace with your actual PAT
$GITHUB_USERNAME = "haidardimas95"      # Your GitHub username
$REPO_NAME = "ujicoba-dashboard"

$GIT_PATH = "C:\Program Files\Git\bin\git.exe"

# Project directory
$PROJECT_DIR = Join-Path $PSScriptRoot "ujicoba-dashboard"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GitHub Push Script for ujicoba-dashboard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location $PROJECT_DIR

# Step 1: Initialize git repository
Write-Host "[1/6] Initializing git repository..." -ForegroundColor Yellow
& $GIT_PATH init
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to initialize git repository" -ForegroundColor Red
    exit 1
}

# Step 2: Add all files
Write-Host "[2/6] Adding files to git..." -ForegroundColor Yellow
& $GIT_PATH add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to add files" -ForegroundColor Red
    exit 1
}

# Step 3: Create initial commit
Write-Host "[3/6] Creating initial commit..." -ForegroundColor Yellow
& $GIT_PATH commit -m "Initial commit: ujicoba-dashboard with Trend-Only Strategy"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to commit" -ForegroundColor Red
    exit 1
}

# Step 4: Create remote (with embedded PAT for authentication)
Write-Host "[4/6] Setting up GitHub remote..." -ForegroundColor Yellow
$REMOTE_URL = "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"
& $GIT_PATH remote remove origin 2>$null
& $GIT_PATH remote add origin $REMOTE_URL
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to set remote" -ForegroundColor Red
    exit 1
}

# Step 5: Push to GitHub
Write-Host "[5/6] Pushing to GitHub..." -ForegroundColor Yellow
& $GIT_PATH branch -M main
& $GIT_PATH push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to push to GitHub" -ForegroundColor Red
    exit 1
}

# Step 6: Verify
Write-Host "[6/6] Verifying deployment..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " SUCCESS! Code pushed to GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Green
Write-Host ""
Write-Host "Next step: Connect to Railway.app" -ForegroundColor Cyan
Write-Host "1. Go to https://railway.app" -ForegroundColor Cyan
Write-Host "2. Click 'New Project'" -ForegroundColor Cyan
Write-Host "3. Select 'Import from GitHub'" -ForegroundColor Cyan
Write-Host "4. Choose repository: $GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host "5. Railway will auto-detect the configuration" -ForegroundColor Cyan
