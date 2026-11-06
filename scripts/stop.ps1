Write-Host "Stopping EEMS services..." -ForegroundColor Cyan

$ports = @(5131, 4200)
foreach ($p in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            try { 
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue 
                Write-Host "   Stopped process $procId on port $p" -ForegroundColor Green
            } catch {}
        }
    }
}

Get-Process -Name "EEMS.Api" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "EEMS services have been stopped." -ForegroundColor Green

