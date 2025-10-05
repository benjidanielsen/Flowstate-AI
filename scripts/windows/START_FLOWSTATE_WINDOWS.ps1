# ========================================
# FlowState-AI One-Click Startup (Windows)
# ========================================
# Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\START_FLOWSTATE_WINDOWS.ps1
# Optional overrides:
#   ... -ApiPort 3011 -FrontendPort 3010 -PythonApiPort 8010

param(
  [int]$ApiPort = 0,        # VSCode Backend API (ai_gods.vscode_backend_api_v2)  default: 3001/3011/3021
  [int]$FrontendPort = 0,   # godmode-frontend server (if applicable)            default: 3000/3010/3020
  [int]$PythonApiPort = 0   # python-worker FastAPI/uvicorn (if it supports it)  default: 8000/8010/8020
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " FlowState-AI CRM System" -ForegroundColor Cyan
Write-Host " One-Click Startup for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------- Encoding fixes (emoji-safe logs) ----------
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

Write-Host "[OK] UTF-8 console + Python I/O set." -ForegroundColor Green

# ---------- Helpers ----------
function Test-PortFree([int]$Port) {
  try {
    $listeners = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
    return -not ($listeners | Where-Object { $_.Port -eq $Port })
  } catch { return $true }
}

function Choose-Port([int]$Preferred, [int[]]$Fallbacks) {
  if ($Preferred -gt 0 -and (Test-PortFree $Preferred)) { return $Preferred }
  $candidates = @()
  if ($Preferred -gt 0) { $candidates += $Preferred }
  $candidates += $Fallbacks
  foreach ($p in $candidates) { if (Test-PortFree $p) { return $p } }
  return $candidates[-1]
}

# ---------- Tool checks ----------
function Assert-Cli($name, $probe, $helpUrl) {
  try { & $probe | Out-Null; Write-Host "[OK] $name found." -ForegroundColor Green }
  catch {
    Write-Host "[ERROR] $name is not installed or not in PATH." -ForegroundColor Red
    if ($helpUrl) { Write-Host "Please install: $helpUrl" -ForegroundColor Yellow }
    Read-Host "Press Enter to exit"
    exit 1
  }
}

Assert-Cli "Python" { python --version 2>&1 } "https://www.python.org/downloads/"
Assert-Cli "Node.js" { node --version 2>&1 }  "https://nodejs.org/"

# ---------- Locate repo root ----------
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$maybeRoot = Resolve-Path (Join-Path $here "..\..") -ErrorAction SilentlyContinue
if ($maybeRoot -and (Test-Path (Join-Path $maybeRoot "ai_gods"))) {
  $ProjectDir = $maybeRoot
} elseif (Test-Path (Join-Path $here "ai_gods")) {
  $ProjectDir = $here
} else {
  $ProjectDir = (Get-Location).Path
}
Set-Location $ProjectDir
Write-Host "[OK] Project root: $ProjectDir" -ForegroundColor Green

# ---------- Activate venv if present ----------
$venv = Join-Path $ProjectDir ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venv) { & $venv; Write-Host "[OK] Virtual environment activated." -ForegroundColor Green }
else { Write-Host "[WARN] .venv not found (continuing with system Python)" -ForegroundColor Yellow }

# ---------- Choose safe ports ----------
$apiPortChosen       = Choose-Port $ApiPort        @(3001, 3011, 3021)
$frontPortChosen     = Choose-Port $FrontendPort   @(3000, 3010, 3020)
$pythonApiPortChosen = Choose-Port $PythonApiPort  @(8000, 8010, 8020)

$env:API_PORT          = "$apiPortChosen"         # Used by ai_gods.vscode_backend_api_v2
$env:BACKEND_API_PORT  = "$apiPortChosen"         # Some code reads this; harmless if ignored
$env:PORT              = "$frontPortChosen"       # Common Node/Vite port var
$env:PYTHON_API_PORT   = "$pythonApiPortChosen"   # If python-worker honors it

# Make python-worker imports resolve (services/*)
$pwSrc = Join-Path $ProjectDir "python-worker\src"
if (Test-Path $pwSrc) { $env:PYTHONPATH = $pwSrc; Write-Host "[OK] PYTHONPATH set for python-worker: $env:PYTHONPATH" -ForegroundColor Green }

Write-Host ""
Write-Host "Selected ports:" -ForegroundColor Cyan
Write-Host ("  VSCode Backend API : http://localhost:{0}" -f $env:API_PORT)
Write-Host ("  Frontend (if used) : http://localhost:{0}" -f $env:PORT)
Write-Host ("  Python API (if used): http://localhost:{0}" -f $env:PYTHON_API_PORT)
Write-Host ""

# ---------- Dependencies ----------
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installing Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Test-Path "requirements.txt") {
  Write-Host "[1/3] pip install -r requirements.txt" -ForegroundColor Yellow
  python -m pip install -r requirements.txt
}

if (Test-Path "python-worker\requirements.txt") {
  Write-Host "[2/3] pip install -r python-worker\requirements.txt" -ForegroundColor Yellow
  python -m pip install -r python-worker\requirements.txt
}

if (Test-Path "godmode-frontend\package.json") {
  if (-not (Test-Path "godmode-frontend\node_modules")) {
    Write-Host "[3/3] npm ci (godmode-frontend)" -ForegroundColor Yellow
    pushd godmode-frontend; npm ci; popd
  } else {
    Write-Host "[OK] godmode-frontend deps already installed." -ForegroundColor Green
  }
}

# Optional classic frontend build
if (Test-Path "frontend\package.json") {
  Write-Host ""; Write-Host "Building classic frontend (if not built)..." -ForegroundColor Yellow
  pushd frontend
  if (-not (Test-Path "dist")) { npm run build } else { Write-Host "[OK] Frontend already built" -ForegroundColor Green }
  popd
}

# ---------- Docker services (guarded) ----------
if (Test-Path "docker-compose.yml") {
  Write-Host ""; Write-Host "Starting Docker services (Redis/Postgres/etc.)..." -ForegroundColor Yellow
  docker-compose up -d
  if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] docker-compose returned a non-zero exit code. Ensure Docker Desktop is running." -ForegroundColor Yellow
  } else {
    Write-Host "[OK] Docker services started (detached)." -ForegroundColor Green
  }
} else {
  Write-Host "[INFO] docker-compose.yml not found. Skipping Docker startup." -ForegroundColor Yellow
}

# ---------- Launch Orchestrator (manages all components) ----------
Write-Host ""; Write-Host "Starting GODMODE Orchestrator v2..." -ForegroundColor Green

Start-Process -FilePath "cmd.exe" `
  -ArgumentList '/k', 'title GODMODE Orchestrator v2 && python -m ai_gods.godmode_orchestrator_v2' `
  -WorkingDirectory $ProjectDir `
  -WindowStyle Minimized

Start-Sleep -Seconds 2

# ---------- Final output ----------
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " System is starting up..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Give it ~10–20 seconds to settle. Then try:" -ForegroundColor Yellow
Write-Host ("  Frontend (if used) : http://localhost:{0}" -f $env:PORT)
Write-Host ("  Backend API (VSCode): http://localhost:{0}" -f $env:API_PORT)
Write-Host ("  Python API (if used): http://localhost:{0}/docs" -f $env:PYTHON_API_PORT)
Write-Host "  Dashboard (if started by orchestrator): http://localhost:3333"
Write-Host ""
Write-Host "All services run in background windows. To stop, close that window, or use your STOP script." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close this launcher (services keep running)"
