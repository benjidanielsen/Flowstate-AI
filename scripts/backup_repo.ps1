param(
    [string]$repoPath = "C:\Flowstate Project\Flowstate-AI",
    [string]$dest = "archive/backups"
)

Set-StrictMode -Version Latest
if (-not (Test-Path -LiteralPath $repoPath)) { Write-Error "repoPath not found: $repoPath"; exit 1 }
Set-Location -LiteralPath $repoPath

$ts = Get-Date -Format yyyyMMddHHmmss
$backupDir = Join-Path -Path $repoPath -ChildPath $dest
if (-not (Test-Path -LiteralPath $backupDir)) { New-Item -ItemType Directory -Path $backupDir -Force | Out-Null }
$archiveFile = Join-Path -Path $backupDir -ChildPath ("backup_{0}.zip" -f $ts)

Write-Host "Creating repo archive: $archiveFile"
Compress-Archive -Path (Get-ChildItem -Path $repoPath -Force | Where-Object { $_.FullName -ne $archiveFile }) -DestinationPath $archiveFile -Force
Write-Host "Backup saved to: $archiveFile"
