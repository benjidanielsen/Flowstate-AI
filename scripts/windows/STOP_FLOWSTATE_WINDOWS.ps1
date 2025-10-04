# ========================================
# FlowState-AI One-Click Shutdown (PowerShell)
# ========================================
# Gracefully stops the services started by START_FLOWSTATE_WINDOWS.ps1

Write-Host "" 
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Stopping FlowState-AI Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$patterns = @(
    'ai-gods/godmode_orchestrator_v2.py',
    'ai-gods/communication_hub_v2.py',
    'ai-gods/project_manager_v2.py',
    'ai-gods/autonomous_development_v2.py',
    'python-worker/worker.py',
    'godmode-dashboard/app_enhanced.py',
    'MANUS_SYNC_ENGINE_ENHANCED.py',
    'backend/src/main.py',
    'frontend/server.js'
)

$stopped = 0

try {
    # First pass: find processes by command line patterns, but exclude VS Code and Electron
    $processesToStop = Get-CimInstance Win32_Process | Where-Object {
        $cmd = $_.CommandLine
        $name = $_.Name
        if (-not $cmd) { return $false }
        # Exclude VS Code, Electron, and related processes
        if ($name -like "*Code.exe*" -or $name -like "*electron*" -or $cmd -like "*vscode*" -or $cmd -like "*Code*" -or $cmd -like "*Electron*" -or $cmd -like "*VS Code*") {
            return $false
        }
        foreach ($pattern in $patterns) {
            if ($cmd -like "*${pattern}*") {
                # Exclude the stop script itself
                if ($cmd -notlike "*STOP_FLOWSTATE_WINDOWS.ps1*") {
                    return $true
                }
            }
        }
        return $false
    }

    foreach ($proc in $processesToStop) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
            Write-Host ("[OK] Stopped {0} (PID {1})" -f $proc.Name, $proc.ProcessId) -ForegroundColor Green
            $stopped += 1
        } catch {
            Write-Host ("[WARN] Unable to stop PID {0}: {1}" -f $proc.ProcessId, $_.Exception.Message) -ForegroundColor Yellow
        }
    }

    # Fallback: terminate listeners on key ports
    $ports = 3000, 3001, 3333, 8000
    foreach ($port in $ports) {
        try {
            $connections = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction Stop
            foreach ($conn in $connections) {
                try {
                    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction Stop
                    Write-Host ("[OK] Cleared port {0} (PID {1})" -f $port, $conn.OwningProcess) -ForegroundColor Green
                    $stopped += 1
                } catch {
                    Write-Host ("[WARN] Unable to clear port {0}: {1}" -f $port, $_.Exception.Message) -ForegroundColor Yellow
                }
            }
        } catch {
            # Ignore errors when no connection exists
        }
    }
} catch {
    Write-Host ("[ERROR] Failed to enumerate processes: {0}" -f $_.Exception.Message) -ForegroundColor Red
}

if ($stopped -eq 0) {
    Write-Host "No FlowState-AI processes were running." -ForegroundColor Yellow
} else {
    Write-Host "" 
    Write-Host ("Total processes stopped: {0}" -f $stopped) -ForegroundColor Cyan
}

Write-Host "" 
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Shutdown complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
