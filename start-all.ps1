<#
.SYNOPSIS
Starts developer services in the recommended order on Windows:
- Ensure OpenSSH Agent is running and keys are loaded
- Start backend (node backend/dist/index.js)
- Wait for backend to accept connections on port 3001
- Serve frontend `frontend/dist` (static files)
- Start the `.multicoder/task/agent_runner.py` as a background job

Usage: Run from the repository root in PowerShell (non-admin):
  .\start-all.ps1

Optional parameters:
  -RunAgent -RunTests -FrontendPort <int>
#>

param(
    [switch]$RunAgent,
    [switch]$RunTests,
    [int]$FrontendPort = 5173
)

Set-StrictMode -Version Latest

function Start-OpenSshAgent {
    Write-Host "[start-all] Ensuring OpenSSH Agent service is running..."
    $svc = Get-Service -Name ssh-agent -ErrorAction SilentlyContinue
    if (-not $svc) {
        Write-Warning "ssh-agent service not found. If you rely on Git-for-Windows agent, ensure you launch from Git Bash."
        return $false
    }
    if ($svc.Status -ne 'Running') {
        try {
            Start-Service ssh-agent -ErrorAction Stop
            Write-Host "[start-all] ssh-agent started"
        } catch {
            Write-Warning "Failed to start ssh-agent: $_"
            return $false
        }
    } else {
        Write-Host "[start-all] ssh-agent already running"
    }

    # Try to add default keys if any
    $keys = @()
    $userProfile = $env:USERPROFILE
    $keyCandidates = @("$userProfile\\.ssh\\id_ed25519", "$userProfile\\.ssh\\id_rsa", "$userProfile\\.ssh\\id_ecdsa")
    foreach ($k in $keyCandidates) {
        if (Test-Path $k) { $keys += $k }
    }
    if ($keys.Count -eq 0) {
        Write-Host "[start-all] No default SSH keys found under $userProfile\.ssh"
    } else {
        foreach ($k in $keys) {
            try {
                # `ssh-add` prints to stdout; log errors to a file for debugging
                & ssh-add $k 2>>"$env:USERPROFILE\.ssh\ssh-add-errors.log"
                Write-Host "[start-all] Added key: $k"
            } catch { $e = $_; Write-Warning ("ssh-add failed for {0}: {1}" -f $k, $e.ToString()) }
        }
    }
    return $true
}

function Start-Backend {
    param(
        [string]$NodeCmd = 'node',
        [string]$BackendEntry = 'backend\\dist\\index.js',
        [int]$Port = 3001
    )

    Write-Host "[start-all] Starting backend ($BackendEntry)"
    $log = Join-Path -Path (Get-Location) -ChildPath 'backend_start.log'
    if (Test-Path $log) { Remove-Item $log -ErrorAction SilentlyContinue }

    $startInfo = @{ }
    $startInfo.FilePath = $NodeCmd
    $startInfo.ArgumentList = @($BackendEntry)
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.UseNewWindow = $false

    $proc = Start-Process @startInfo -PassThru
    Write-Host "[start-all] Backend process id: $($proc.Id)"

    # Wait for TCP port to be open
    $maxWait = 60
    $waited = 0
    while ($waited -lt $maxWait) {
        try {
            $sock = New-Object System.Net.Sockets.TcpClient
            $async = $sock.BeginConnect('127.0.0.1', $Port, $null, $null)
            $ok = $async.AsyncWaitHandle.WaitOne(1000)
            if ($ok -and $sock.Connected) {
                $sock.Close()
                Write-Host "[start-all] Backend is responding on port $Port"
                return $proc
            }
        } catch {
            Write-Verbose "[start-all] Backend connection attempt failed: $($_.Exception.Message)"
        }
        Start-Sleep -Seconds 1
        $waited += 1
        Write-Host -NoNewline '.'
    }
    Write-Warning "[start-all] Backend did not respond within $maxWait seconds"
    return $proc
}

function Start-FrontendStatic {
    param(
        [int]$Port = 5173,
        [string]$DistPath = 'frontend\\dist'
    )
    $full = Join-Path (Get-Location) $DistPath
    if (-not (Test-Path $full)) {
        Write-Warning "Frontend dist not found at $full. Skipping frontend start."
        return $null
    }

    Write-Host "[start-all] Serving frontend from $full on port $Port"
    # Prefer `npx serve` if available, otherwise fallback to Python http.server

    # Initialize variables to avoid uninitialized/unused-variable diagnostics
    # changed: use $cmd as the executable variable name so any previous assignment to $cmd will be used
    $cmd = $null
    $args = $null
    $workingDir = $null

    if (Get-Command npx -ErrorAction SilentlyContinue) {
        $cmd = (Get-Command npx -ErrorAction SilentlyContinue).Source
        $args = @('serve','-s',$full,'-l',$Port)
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $cmd = (Get-Command python -ErrorAction SilentlyContinue).Source
        $args = @('-m','http.server',$Port)
        $workingDir = $full
    } else {
        Write-Warning "No suitable static server found (npx or python). Serve `frontend/dist` manually."
        return $null
    }

    if ($cmd) {
        if ($workingDir) {
            $ps = Start-Process -FilePath $cmd -ArgumentList $args -WorkingDirectory $workingDir -NoNewWindow -PassThru
        } else {
            $ps = Start-Process -FilePath $cmd -ArgumentList $args -NoNewWindow -PassThru
        }

        Write-Host "[start-all] Launched $cmd (pid $($ps.Id))"
        return $ps
    } else {
        Write-Warning "Failed to determine executable for serving frontend."
        return $null
    }
}

function Start-AgentRunner {
    param(
        [string]$RunnerPath = '.multicoder\\task\\agent_runner.py',
        [switch]$RunTests = $false
    )
    $full = Join-Path (Get-Location) $RunnerPath
    if (-not (Test-Path $full)) {
        Write-Warning "Agent runner not found at $full. Skipping."
        return $null
    }
    $runnerArgs = @()
    if ($RunTests) { $runnerArgs += '--run-tests' }
    # Run as a background job and redirect output
    $log = Join-Path (Get-Location) '.multicoder\\task\\agent_runner.log'
    Write-Host "[start-all] Starting agent runner as background job; logging -> $log"
    $sb = {
        param($fullPath, $runnerArgs, $logPath, $pythonPath)
        & $pythonPath $fullPath @runnerArgs *>&1 | Out-File -FilePath $logPath -Encoding utf8 -Append
    }
    # Choose python executable (prefer `python` on PATH)
    $py = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
    if (-not $py) { Write-Warning 'No python executable found on PATH; cannot start runner.'; return $null }

    # changed: use $jobName and use it when creating the job so the assigned variable is used
    $jobName = "agent_runner_{0}" -f ([System.Guid]::NewGuid().ToString('N').Substring(0,8))

    $job = Start-Job -Name $jobName -ScriptBlock $sb -ArgumentList @($full, $runnerArgs, $log, $py)
    Write-Host "[start-all] Agent runner job id: $($job.Id); name: $jobName"
    return $job
}


# --- Main ---
Push-Location (Get-Location)
try {
    Start-OpenSshAgent | Out-Null

    $backendProc = Start-Backend

    # Optionally run backend tests once to validate
    if ($RunTests) {
        Write-Host "[start-all] Running backend tests once..."
        Push-Location (Join-Path (Get-Location) 'backend')
        if (Get-Command npm -ErrorAction SilentlyContinue) {
            npm run test
        } else {
            Write-Warning 'npm not found; skipping test run.'
        }
        Pop-Location
    }

    $frontendProc = Start-FrontendStatic -Port $FrontendPort

    $agentJob = $null
    if ($RunAgent) { $agentJob = Start-AgentRunner -RunTests:$RunTests }

    # Collect process and job IDs for easier cleanup
    $serviceInfo = @{
        BackendPid  = if ($backendProc) { $backendProc.Id } else { $null }
        FrontendPid = if ($frontendProc) { $frontendProc.Id } else { $null }
        AgentJobId  = if ($agentJob) { $agentJob.Id } else { $null }
        AgentJobName = if ($agentJob) { $agentJob.Name } else { $null }
    }
    $serviceInfo | ConvertTo-Json | Set-Content -Path "started-services.json" -Encoding UTF8

    Write-Host "[start-all] All requested services started. Backend pid: $($serviceInfo.BackendPid); Frontend pid: $($serviceInfo.FrontendPid); Agent job id: $($serviceInfo.AgentJobId)"
    Write-Host "[start-all] To stop all: run .\stop-all.ps1 (provided in repo) or use:"
    Write-Host "    Stop-Process -Id $($serviceInfo.BackendPid) -Force"
    Write-Host "    Stop-Process -Id $($serviceInfo.FrontendPid) -Force"
    if ($serviceInfo.AgentJobId) {
        Write-Host "    Stop-Job -Id $($serviceInfo.AgentJobId); Remove-Job -Id $($serviceInfo.AgentJobId)"
    }
    Write-Host "[start-all] (Service info written to started-services.json)"
} finally {
    Pop-Location
}
