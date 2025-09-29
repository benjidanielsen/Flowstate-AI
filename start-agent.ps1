# Start the agent runner as a background job and log output
# Usage: Run this from the repo root in PowerShell

$python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
$script = Join-Path -Path $PSScriptRoot -ChildPath '.multicoder\task\agent_runner.py'
$log = Join-Path -Path $PSScriptRoot -ChildPath '.multicoder\task\agent_runner.log'

if (-not (Test-Path $python)) {
    # Fallback to python on PATH
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
}

if (-not $python) {
    Write-Error "Python executable not found. Please install Python 3.10+ or adjust the script to point to your python.exe"
    exit 1
}

$jobScript = {
    param($py, $scriptPath, $logPath)
    & $py $scriptPath --interval 600 --run-tests 2>&1 | Tee-Object -FilePath $logPath
}

Start-Job -Name FlowstateAgent -ScriptBlock $jobScript -ArgumentList $python, $script, $log
Write-Output "Started FlowstateAgent job; logs will be appended to $log"
