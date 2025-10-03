# GODMODE Local Setup

This guide captures the minimum steps to bring the GODMODE/AI-gods tooling online with human oversight.

## 1. Install Python 3.12 dependencies

```powershell
python -m venv .godmode-venv
.godmode-venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r ai-gods/requirements.txt
pip install -r godmode-dashboard/requirements.txt
```

> Tip: Keep this virtual environment dedicated to the GODMODE services so the worker (FastAPI) venv stays isolated.

## 2. Prepare Node services

```powershell
npm install
npm run build # optional sanity check
```

## 3. Launch services with oversight

Use the helper script added at repo root:

```powershell
# Dry run to review commands
./start-godmode.ps1 -DryRun

# Start backend, frontend, python worker, and GODMODE dashboard
./start-godmode.ps1

# Include the autonomous project manager too
./start-godmode.ps1 -Targets all
```

Each component opens in its own PowerShell window and writes logs to `godmode-logs/<component>.log`. Stop any component with `Stop-Process -Id <pid>`.

## 4. Verify the stack

- Backend API health: http://localhost:3001/api/health
- Frontend dashboard: http://localhost:3000
- Python worker docs: http://localhost:8000/docs
- GODMODE oversight UI: http://localhost:3333

## 5. Ongoing checks

- Tail logs in `godmode-logs/` to monitor agent activity.
- Keep branch protections in GitHub so project-manager commits remain review-gated.
- Before enabling `project-manager`, confirm GitHub token scopes and repository protections.

## 6. Shut down

Close the spawned PowerShell windows or terminate specific processes:

```powershell
Get-Process | Where-Object { $_.ProcessName -like 'powershell' -and $_.MainWindowTitle -like 'Flowstate*' }
Stop-Process -Id <pid>
```

Deactivate the venv when finished:

```powershell
Deactivate
```
