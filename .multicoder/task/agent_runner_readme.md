Agent runner for Flowstate-AI (.multicoder/task)

Overview

This runner is a small, safe automation that repeatedly executes the repo scanning and optional backend tests. It's intended for developer convenience and must be run manually by you. It only writes under `.multicoder/task/` and the project directory.

Files created

- `.multicoder/task/agent_runner.py` - main runner script
- `.multicoder/task/scan.py` - (existing) scanner script used by runner
- `.multicoder/task/implementation_log.json` - auto-appended log entries
- `.multicoder/task/scan_last_run.log` - last scan stdout/stderr
- `.multicoder/task/test_last_run.log` - last test stdout/stderr (if enabled)
- `.multicoder/task/next_tasks.md` - generated short task list

How to run

One-off:

```powershell
cd 'C:\Users\binya\OneDrive\Music\Flowstate-AI'
python .\.multicoder\task\agent_runner.py --once
```

Continuous (10-minute interval):

```powershell
cd 'C:\Users\binya\OneDrive\Music\Flowstate-AI'
python .\.multicoder\task\agent_runner.py --interval 600 --run-tests
```

Monitoring

Tail the main implementation log:

```powershell
Get-Content .\.multicoder\task\implementation_log.json -Wait -Tail 20
```

Stop

Use Ctrl+C when running interactively, or stop the background PowerShell job you created.

Safety

- Runner never pushes to Git.
- Runner avoids touching system-wide files; it operates under the repo root and `.multicoder/task`.

If you want an equivalent PowerShell wrapper (Start-Job), say so and I'll add it.
