# Flowstate-AI: CLEANUP dry run

This document summarizes the dry-run repo audit and recommended cleanup steps. No destructive changes are performed by the scripts in `/scripts` unless explicitly requested.

## Key observations (from local audit)

- Local `.venv` exists and is large (≈1.3GB). It should be excluded from the repo and removed from git index if tracked.
- `node_modules/` and `frontend/node_modules` are large but normally gitignored. Verify they are excluded by `.gitignore`.
- `godmode-logs/` and `GODMODE-BACKUP/` contain runtime logs and backups; they should be excluded or moved to `archive/`.
- Temporary audit files (e.g., `tmp_file_sizes.csv`, `tmp_git_ls_files.txt`) are present and should be ignored.
- There are reparse points (symlinks) inside `node_modules` that may link outside the repo; confirm they are intentional.

## Recommended changes (no-op unless you approve)

1. Add `.venv/`, `tmp_*`, `*.csv`, `GODMODE-BACKUP/`, and `godmode-logs/` to `.gitignore`.
2. If `.venv` or other noisy directories are tracked, remove them from the index: `git rm -r --cached .venv` and re-commit. This untracks files but preserves them on disk.
3. Move large historical or raw docs to `docs/raw_archive/` and add that path to `.gitignore` if they are not essential for active development.
4. Create `archive/` for backups and add an archive script to cleanly move old logs or large binary files outside the active repository.

## Next steps (approve before applying)

Run `scripts/cleanup_dryrun.ps1` to produce a full report and an actionable command list. To actually apply the changes, re-run with the `-apply` flag (careful—this will modify `.gitignore` and run `git rm --cached` for tracked items).

## Non-destructive commands to run locally to replicate the audit

```powershell
Set-Location 'C:\Flowstate Project\Flowstate-AI'
# show tracked differences
git status --porcelain --untracked-files=all
# show top 20 largest files
Get-ChildItem -Path . -Recurse -File | Sort-Object Length -Descending | Select-Object -First 20 FullName,Length
# show symlinks
Get-ChildItem -Recurse -Force | Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }
```

## Legal & Safety

Do not run destructive scripts on production clones. Back up the repository before applying `git rm` or `git reset --hard`.
