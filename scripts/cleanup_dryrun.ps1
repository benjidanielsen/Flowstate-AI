param(
    [switch]$apply
)

Set-StrictMode -Version Latest
$repoPath = 'C:\Flowstate Project\Flowstate-AI'
if (-not (Test-Path -LiteralPath $repoPath)) { Write-Host "ERROR: repoPath not found: $repoPath"; exit 1 }
Set-Location -LiteralPath $repoPath

Write-Host "=== Repo Cleanup Dry Run ==="
Write-Host "Repo: $repoPath"

Write-Host "Counting files and top offenders..."
$files = Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue
Write-Host ('Found files: ' + ($files | Measure-Object).Count)

Write-Host "Top 30 largest files (FullPath, bytes):"
$largest = $files | Sort-Object Length -Descending | Select-Object FullName, Length -First 30
$largest | ForEach-Object { Write-Host ($_.FullName + ',' + $_.Length) }

Write-Host "Noisy directories to consider: .venv, node_modules, godmode-logs, GODMODE-BACKUP"
foreach ($d in @('.venv', 'node_modules', 'frontend\node_modules', 'godmode-logs', 'GODMODE-BACKUP')) {
    if (Test-Path $d) { $size = (Get-ChildItem -Path $d -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum; Write-Host ("$d : $size bytes") } else { Write-Host ("$d : not present") }
}

Write-Host "Detected reparse points/junctions and potential symlinks:"
Get-ChildItem -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 } | Select-Object FullName, Attributes | Format-Table -AutoSize

Write-Host "Suggested gitignore entries (verify):"
$suggested = @('.venv/', 'tmp_*', '*.csv', 'GODMODE-BACKUP/', 'godmode-logs/')
$suggested | ForEach-Object { Write-Host "  $_" }

Write-Host "Suggested git commands (no-op until you approve):"
Write-Host "  # Append suggested patterns to .gitignore if not present"
Write-Host "  # git add .gitignore && git commit -m 'chore: ignore local virtual env, tmp files, logs'"
Write-Host "  # If .venv is tracked: git rm -r --cached .venv && git commit -m 'chore: untrack .venv'"
Write-Host "  # Optionally: move big files to archive/ and add an entry: 'archive/' to .gitignore"

if ($apply) {
    Write-Host "APPLY: Append suggested entries to .gitignore and run git rm --cached for tracked noisy directories"
    # Append entries to .gitignore if missing
    foreach ($line in $suggested) {
        if (-not (Select-String -Path .gitignore -Pattern ([Regex]::Escape($line)) -Quiet)) {
            Add-Content -Path .gitignore -Value $line
            Write-Host "Appended $line to .gitignore"
        }
        else {
            Write-Host "$line already present in .gitignore"
        }
    }
    # If .venv is tracked, remove from index
    if (git ls-files --error-unmatch .venv 2>$null) {
        Write-Host ".venv is tracked; removing from index (git rm -r --cached .venv)"
        git rm -r --cached .venv
    }
    else { Write-Host ".venv not tracked by git" }
    Write-Host "Apply phase complete. Please inspect changes and commit them if acceptable."
}
else {
    Write-Host "Dry-run mode. To apply changes, rerun with -apply"
}
