#!/usr/bin/env python3
"""
Agent runner for Flowstate-AI .multicoder tasks.

Behavior:
- Runs .multicoder/task/scan.py each iteration (or once with --once)
- Optionally runs backend tests with --run-tests
- Appends a structured entry to .multicoder/task/implementation_log.json for each iteration
- Writes per-run logs: scan_last_run.log and test_last_run.log
- Safe defaults: only writes under .multicoder/task/ and runs local commands

Usage:
  python ./.multicoder/task/agent_runner.py [--once] [--interval SECONDS] [--run-tests]

"""

import argparse
import subprocess
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import sys

ROOT = Path(__file__).resolve().parents[2]  # repo root
TASK_DIR = ROOT / '.multicoder' / 'task'
SCAN_PY = TASK_DIR / 'scan.py'
LOG_JSON = TASK_DIR / 'implementation_log.json'
SCAN_LOG = TASK_DIR / 'scan_last_run.log'
TEST_LOG = TASK_DIR / 'test_last_run.log'
NEXT_TASKS = TASK_DIR / 'next_tasks.md'
EXTRACTED = TASK_DIR / 'extracted_tasks.json'

TASK_DIR.mkdir(parents=True, exist_ok=True)

def append_log(entry: Dict[str, Any]) -> None:
    LOG_JSON.parent.mkdir(parents=True, exist_ok=True)
    data: List[Any] = []
    if LOG_JSON.exists():
        try:
            with LOG_JSON.open('r', encoding='utf8') as f:
                data = json.load(f)
        except Exception:
            # If file corrupt, preserve by renaming
            backup = LOG_JSON.with_suffix('.corrupt-'+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')+'.json')
            LOG_JSON.rename(backup)
            data = []
    data.append(entry)
    with LOG_JSON.open('w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_scan() -> Dict[str, Any]:
    if not SCAN_PY.exists():
        msg = f'scan.py not found at {SCAN_PY}. Skipping scan.'
        with SCAN_LOG.open('a', encoding='utf8') as f:
            f.write(msg + '\n')
        return {'ok': False, 'error': msg}
 
    cmd = [sys.executable, str(SCAN_PY)]
    start = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=60*10)
        out = proc.stdout
        err = proc.stderr
        rc = proc.returncode
        with SCAN_LOG.open('w', encoding='utf8') as f:
            f.write(f'[{start}] CMD: {cmd}\n')
            f.write('--- STDOUT ---\n')
            f.write(out or '')
            f.write('\n--- STDERR ---\n')
            f.write(err or '')
            f.write('\n')
        return {'ok': rc == 0, 'returncode': rc, 'stdout': out, 'stderr': err}
    except Exception as e:
        with SCAN_LOG.open('a', encoding='utf8') as f:
            f.write(f'Exception running scan: {e}\n')
        return {'ok': False, 'error': str(e)}


def run_backend_tests() -> Dict[str, Any]:
    # Runs `npm run test` in backend; safe and optional
    backend_dir = ROOT / 'backend'
    if not backend_dir.exists():
        msg = 'backend directory not found; skipping tests'
        with TEST_LOG.open('a', encoding='utf8') as f:
            f.write(msg + '\n')
        return {'ok': False, 'error': msg}
 
    cmd = ['npm', 'run', 'test', '--silent']
    start = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(backend_dir), timeout=60*5)
        out = proc.stdout
        err = proc.stderr
        rc = proc.returncode
        with TEST_LOG.open('w', encoding='utf8') as f:
            f.write(f'[{start}] CMD: {cmd}\n')
            f.write('--- STDOUT ---\n')
            f.write(out or '')
            f.write('\n--- STDERR ---\n')
            f.write(err or '')
            f.write('\n')
        return {'ok': rc == 0, 'returncode': rc, 'stdout': out, 'stderr': err}
    except Exception as e:
        with TEST_LOG.open('a', encoding='utf8') as f:
            f.write(f'Exception running backend tests: {e}\n')
        return {'ok': False, 'error': str(e)}


def update_next_tasks_from_extracted() -> bool:
    # Simple heuristic: if extracted_tasks.json exists and next_tasks.md missing or older, copy top N
    try:
        if EXTRACTED.exists():
            with EXTRACTED.open('r', encoding='utf8') as f:
                data = json.load(f)
            # Expect data to be a list of task objects with 'summary' or similar
            lines = ['# Next tasks (auto-extracted)\n']
            for i, t in enumerate(data[:10], 1):
                summary = t.get('summary') if isinstance(t, dict) else str(t)
                lines.append(f'{i}. {summary}\n')
            NEXT_TASKS.write_text('\n'.join(lines), encoding='utf8')
            return True
    except Exception:
        # ignore problems reading/parsing extracted tasks
        return False
    return False


def make_log_entry(action: str, details: Any) -> Dict[str, Any]:
    return {
        'time': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'action': action,
        'details': details
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='Run one iteration and exit')
    parser.add_argument('--interval', type=int, default=600, help='Seconds between iterations (default 600)')
    parser.add_argument('--run-tests', action='store_true', help='Run backend tests after scan')
    args = parser.parse_args()
 
    iteration = 0
    try:
        while True:
            iteration += 1
            entry: Dict[str, Any] = {'iteration': iteration, 'time': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'), 'results': {}}
            # Run scan
            scan_res = run_scan()
            entry['results']['scan'] = scan_res

            # Optionally run backend tests
            if args.run_tests:
                test_res = run_backend_tests()
                entry['results']['tests'] = test_res
            else:
                entry['results']['tests'] = {'skipped': True}

            # Update next_tasks.md if possible
            try:
                updated = update_next_tasks_from_extracted()
                entry['results']['next_tasks_updated'] = updated
            except Exception:
                entry['results']['next_tasks_updated'] = False

            # Append log
            log_entry = make_log_entry('iteration_complete', entry)
            append_log(log_entry)

            # Print a short status to stdout so interactive users see progress
            status = 'OK' if entry['results']['scan'].get('ok') else 'FAIL'
            status += ' (tests skipped)' if not args.run_tests else ''
            print(f'[{datetime.now().astimezone().isoformat()}] Iteration {iteration} completed: {status}')

            if args.once:
                break

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\nAgent runner interrupted by user (KeyboardInterrupt)')
    except Exception as e:
        append_log(make_log_entry('runner_exception', {'error': str(e)}))
        raise


if __name__ == '__main__':
    main()
    main()
