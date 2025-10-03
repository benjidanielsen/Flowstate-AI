Param(
    [switch]$SkipNode,
    [switch]$SkipE2E
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

function Invoke-Step {
    param(
        [string]$Title,
        [scriptblock]$Action
    )
    Write-Host "`n===== $Title =====" -ForegroundColor Cyan
    & $Action
}

Invoke-Step -Title 'Python compile check' -Action {
    python -m compileall `
        ai-gods/error_handling.py `
        ai-gods/project_manager_config.py `
        ai-gods/project_manager_enhanced.py `
        ai-gods/godmode_brain.py
}

Invoke-Step -Title 'Python unit tests' -Action {
    python -m unittest discover -s tests -p 'test_*.py'
}

Invoke-Step -Title 'GODMODE health checks' -Action {
    python ai-gods/project_manager_enhanced.py --health-check
    python ai-gods/project_manager_enhanced.py --demo
    python ai-gods/godmode_brain.py --show-plan | Out-Null
}

if (-not $SkipNode) {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Warning "Skipping Node.js steps because npm is not available. Use -SkipNode to silence this warning."
    }
    else {
        Invoke-Step -Title 'Node.js lint' -Action {
            npm run lint
        }
        Invoke-Step -Title 'Node.js build' -Action {
            npm run build
        }
    }
}

if (-not $SkipE2E) {
    if (-not (Get-Command playwright -ErrorAction SilentlyContinue)) {
        Write-Warning "Skipping Playwright tests because the CLI is not installed. Use -SkipE2E to silence this warning."
    }
    else {
        Invoke-Step -Title 'E2E smoke tests' -Action {
            npx playwright test --config=playwright.config.ts --reporter=list
        }
    }
}

Write-Host "`nSystem check completed" -ForegroundColor Green
