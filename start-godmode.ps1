param(
    [ValidateSet(''backend'',''frontend'',''worker'',''dashboard'',''project-manager'',''all'', IgnoreCase = $true)]
    [string[]]$Targets = @(''backend'',''frontend'',''worker'',''dashboard''),
    [switch]$DryRun
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $projectRoot) {
    $projectRoot = Get-Location
}
$logsDir = Join-Path $projectRoot 'godmode-logs'
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$componentMap = [ordered]@{
    'backend' = [ordered]@{
        Title = 'Flowstate Backend'
        WorkingDirectory = $projectRoot
        Command = 'npm run dev:backend'
        Log = Join-Path $logsDir 'backend.log'
        Description = 'Node/Express API on http://localhost:3001'
    }
    'frontend' = [ordered]@{
        Title = 'Flowstate Frontend'
        WorkingDirectory = Join-Path $projectRoot 'frontend'
        Command = 'npm run dev'
        Log = Join-Path $logsDir 'frontend.log'
        Description = 'React dashboard on http://localhost:3000'
    }
    'worker' = [ordered]@{
        Title = 'Flowstate Python Worker'
        WorkingDirectory = Join-Path $projectRoot 'python-worker'
        Command = 'uvicorn src.main:app --reload --host 0.0.0.0 --port 8000'
        Log = Join-Path $logsDir 'python-worker.log'
        Description = 'Reminder & NBA service on http://localhost:8000'
    }
    'dashboard' = [ordered]@{
        Title = 'GODMODE Dashboard'
        WorkingDirectory = Join-Path $projectRoot 'godmode-dashboard'
        Command = 'python app_enhanced.py'
        Log = Join-Path $logsDir 'godmode-dashboard.log'
        Description = 'Oversight UI on http://localhost:3333'
    }
    'project-manager' = [ordered]@{
        Title = 'GODMODE Project Manager'
        WorkingDirectory = Join-Path $projectRoot 'ai-gods'
        Command = 'python project-manager.py'
        Log = Join-Path $logsDir 'project-manager.log'
        Description = 'Main AI orchestrator (optional)'
    }
}

if ($Targets -contains 'all') {
    $selected = $componentMap.Keys
} else {
    $selected = @()
    foreach ($target in $Targets) {
        $key = $target.ToLower()
        if (-not $componentMap.Contains($key)) {
            Write-Error "Unknown component '$target'."
            exit 1
        }
        if ($selected -notcontains $key) {
            $selected += $key
        }
    }
}

function Start-GodmodeProcess {
    param(
        [string]$Name,
        [hashtable]$Component,
        [switch]$DryRun
    )

    $cmd = $Component.Command
    $dir = $Component.WorkingDirectory
    $log = $Component.Log
    $title = $Component.Title
    $description = $Component.Description

    Write-Host "[start-godmode] $Name -> $cmd" -ForegroundColor Cyan
    Write-Host "                 $description" -ForegroundColor DarkGray
    if ($DryRun) { return }

    if (-not (Test-Path $dir)) {
        Write-Error "Directory not found: $dir"
        return
    }

    $fullCommand = "[Console]::Title='$title'; Set-Location '$dir'; Write-Host '[start-godmode] $Name ready'; $cmd"

    $process = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList '-NoLogo','-NoProfile','-Command', $fullCommand `
        -WorkingDirectory $dir `
        -PassThru

    $meta = "Started $Name (PID $($process.Id)) -> $cmd"
    $meta | Add-Content -Path $log
    Write-Host "[start-godmode] PID $($process.Id) logging to $log" -ForegroundColor Green
}

foreach ($name in $selected) {
    Start-GodmodeProcess -Name $name -Component $componentMap[$name] -DryRun:$DryRun
}

if (-not $DryRun) {
    Write-Host "\n[start-godmode] Components launched. Logs live under $logsDir" -ForegroundColor Yellow
    Write-Host "Use Stop-Process -Id <pid> to halt a component."
} else {
    Write-Host "[start-godmode] Dry run only: no commands executed." -ForegroundColor Yellow
}
