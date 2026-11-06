[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Clear-Host

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "          EEMS - Election Operations Management Platform            " -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

$root = Split-Path -Parent $PSScriptRoot

# 1. Check prerequisites
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] .NET SDK not found in PATH! Please install .NET 8 SDK." -ForegroundColor Red
    pause
    exit 1
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js / NPM not found in PATH! Please install Node.js." -ForegroundColor Red
    pause
    exit 1
}

# 2. Check and clean up previous processes on ports 5131 or 4200
Write-Host "[*] Checking and freeing ports 5131 and 4200..." -ForegroundColor Gray
$ports = @(5131, 4200)
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            try { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
}
Get-Process -Name "EEMS.Api" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 3. Check PostgreSQL
Write-Host "[1/3] Checking PostgreSQL service..." -ForegroundColor Gray
$pg = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pg) {
    if ($pg.Status -ne 'Running') {
        Write-Host "      Starting PostgreSQL service ($($pg.Name))..." -ForegroundColor Yellow
        try { Start-Service -Name $pg.Name } catch { Write-Host "      Could not start automatically. Ensure DB runs on port 5432." -ForegroundColor Yellow }
    } else {
        Write-Host "      PostgreSQL is running." -ForegroundColor Green
    }
}

# 4. Start Backend API
Write-Host "[2/3] Launching ASP.NET Core 8 Backend API..." -ForegroundColor Gray
$backendDir = Join-Path $root "backend"
Start-Process cmd.exe -ArgumentList "/k", "title EEMS Backend API [Port 5131] && cd /d `"$backendDir`" && dotnet run --project src/EEMS.Api"

# 5. Start Frontend Angular
Write-Host "[3/3] Launching Angular 22 Frontend..." -ForegroundColor Gray
$frontendDir = Join-Path $root "frontend"
Start-Process cmd.exe -ArgumentList "/k", "title EEMS Frontend [Port 4200] && cd /d `"$frontendDir`" && npm start"

# 6. Wait for servers to be ready
Write-Host ""
Write-Host "[*] Waiting for services to initialize..." -ForegroundColor Yellow

$backendReady = $false
$sw = [System.Diagnostics.Stopwatch]::StartNew()
Write-Host "   Waiting for Backend API (http://localhost:5131/health/live)... " -NoNewline
while (-not $backendReady -and $sw.Elapsed.TotalSeconds -lt 45) {
    try {
        $res = Invoke-RestMethod -Uri "http://localhost:5131/health/live" -TimeoutSec 2 -ErrorAction Stop
        if ($res -eq "Healthy") { $backendReady = $true }
    } catch {
        Start-Sleep -Milliseconds 700
    }
}
if ($backendReady) {
    Write-Host "[READY]" -ForegroundColor Green
} else {
    Write-Host "[TIMEOUT - check backend console]" -ForegroundColor Yellow
}

$frontendReady = $false
$sw.Restart()
Write-Host "   Waiting for Frontend compile (http://localhost:4200)... " -NoNewline
while (-not $frontendReady -and $sw.Elapsed.TotalSeconds -lt 45) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:4200" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($res.StatusCode -eq 200) { $frontendReady = $true }
    } catch {
        Start-Sleep -Milliseconds 700
    }
}
if ($frontendReady) {
    Write-Host "[READY]" -ForegroundColor Green
} else {
    Write-Host "[TIMEOUT - check frontend console]" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "                    EEMS SYSTEM IS NOW READY!                       " -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  Web App        : http://localhost:4200" -ForegroundColor White
Write-Host "  Swagger Docs   : http://localhost:5131/swagger" -ForegroundColor White
Write-Host "  Health Live    : http://localhost:5131/health/live" -ForegroundColor White
Write-Host "  Health Ready   : http://localhost:5131/health/ready" -ForegroundColor White
Write-Host ""
Write-Host "  ------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Default Login Credentials:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "     Tenant ID  : 1000000000" -ForegroundColor White
Write-Host "     Username   : admin" -ForegroundColor White
Write-Host "     Password   : EEMS@123456!" -ForegroundColor White
Write-Host "  ------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Launching web browser..." -ForegroundColor Green
Start-Process "http://localhost:4200"

Write-Host ""
Write-Host "(To stop all services, double-click 'stop.bat')" -ForegroundColor Gray

