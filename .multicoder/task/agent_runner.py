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
import os
from typing import Any, Dict, List, cast
import sys

# Reusable constants for timestamp formatting
UTC_OFFSET = '+00:00'
Z_SUFFIX = 'Z'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # repo root
TASK_DIR = os.path.join(ROOT, '.multicoder', 'task')
SCAN_PY = os.path.join(TASK_DIR, 'scan.py')
LOG_JSON = os.path.join(TASK_DIR, 'implementation_log.json')
SCAN_LOG = os.path.join(TASK_DIR, 'scan_last_run.log')
TEST_LOG = os.path.join(TASK_DIR, 'test_last_run.log')
NEXT_TASKS = os.path.join(TASK_DIR, 'next_tasks.md')
EXTRACTED = os.path.join(TASK_DIR, 'extracted_tasks.json')

os.makedirs(TASK_DIR, exist_ok=True)

def append_log(entry: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(LOG_JSON), exist_ok=True)
    data: List[Any] = []
    if os.path.exists(LOG_JSON):
        try:
            with open(LOG_JSON, 'r', encoding='utf8') as f:
                data = json.load(f)
        except Exception:
            # If file corrupt, preserve by renaming
            backup = LOG_JSON + '.corrupt-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S') + '.json'
            try:
                os.replace(LOG_JSON, backup)
            except Exception:
                pass
            data = []
    data.append(entry)
    with open(LOG_JSON, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_scan() -> Dict[str, Any]:
    if not os.path.exists(SCAN_PY):
        msg = f'scan.py not found at {SCAN_PY}. Skipping scan.'
        with open(SCAN_LOG, 'a', encoding='utf8') as f:
            f.write(msg + '\n')
        return {'ok': False, 'error': msg}
 
    cmd = [sys.executable, SCAN_PY]
    start = datetime.now(timezone.utc).isoformat().replace(UTC_OFFSET, Z_SUFFIX)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=60*10)
        out = proc.stdout
        err = proc.stderr
        rc = proc.returncode
        with open(SCAN_LOG, 'w', encoding='utf8') as f:
            f.write(f'[{start}] CMD: {cmd}\n')
            f.write('--- STDOUT ---\n')
            f.write(out or '')
            f.write('\n--- STDERR ---\n')
            f.write(err or '')
            f.write('\n')
        return {'ok': rc == 0, 'returncode': rc, 'stdout': out, 'stderr': err}
    except Exception as e:
        with open(SCAN_LOG, 'a', encoding='utf8') as f:
            f.write(f'Exception running scan: {e}\n')
        return {'ok': False, 'error': str(e)}


def run_backend_tests() -> Dict[str, Any]:
    # Runs `npm run test` in backend; safe and optional
    backend_dir = os.path.join(ROOT, 'backend')
    if not os.path.exists(backend_dir):
        msg = 'backend directory not found; skipping tests'
        with open(TEST_LOG, 'a', encoding='utf8') as f:
            f.write(msg + '\n')
        return {'ok': False, 'error': msg}
 
    # Ensure npm is available on PATH; if not, surface a clear message
    try:
        import shutil
        npm_path = shutil.which('npm')
    except Exception:
        npm_path = None
    if not npm_path:
        msg = 'npm not found; skipping backend tests'
        with open(TEST_LOG, 'a', encoding='utf8') as f:
            f.write(msg + '\n')
        return {'ok': False, 'error': msg}

    cmd = [npm_path, 'run', 'test', '--silent']
    start = datetime.now(timezone.utc).isoformat().replace(UTC_OFFSET, Z_SUFFIX)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=backend_dir, timeout=60*5)
        out = proc.stdout
        err = proc.stderr
        rc = proc.returncode
        with open(TEST_LOG, 'w', encoding='utf8') as f:
            f.write(f'[{start}] CMD: {cmd}\n')
            f.write('--- STDOUT ---\n')
            f.write(out or '')
            f.write('\n--- STDERR ---\n')
            f.write(err or '')
            f.write('\n')
        return {'ok': rc == 0, 'returncode': rc, 'stdout': out, 'stderr': err}
    except Exception as e:
        with open(TEST_LOG, 'a', encoding='utf8') as f:
            f.write(f'Exception running backend tests: {e}\n')
        return {'ok': False, 'error': str(e)}


def update_next_tasks_from_extracted() -> bool:
    # Simple heuristic: if extracted_tasks.json exists and next_tasks.md missing or older, copy top N
    try:
        if os.path.exists(EXTRACTED):
            with open(EXTRACTED, 'r', encoding='utf8') as f:
                raw: Any = json.load(f)
            # Ensure we have a list of dict-like items so `.get` is safe
            if not isinstance(raw, list):
                return False
            # Cast to a typed list so static checkers know the element type in the loop
            raw_list = cast(List[Any], raw)
            data: List[Dict[str, Any]] = []
            for item in raw_list:
                if isinstance(item, dict):
                    # Cast to Dict[Any, Any] so type-checkers know .items() yields (Any, Any)
                    item_dict = cast(Dict[Any, Any], item)
                    # Build a new dict with string keys and Any values
                    converted: Dict[str, Any] = {str(k): v for k, v in item_dict.items()}
                    data.append(converted)
                else:
                    # Ensure a string summary for non-dict items
                    data.append({'summary': str(item)})
            lines = ['# Next tasks (auto-extracted)\n']
            for i, t in enumerate(data[:10], 1):
                summary = t.get('summary', '')
                lines.append(f'{i}. {summary}\n')
            with open(NEXT_TASKS, 'w', encoding='utf8') as f:
                f.write('\n'.join(lines))
            return True
    except Exception:
        # ignore problems reading/parsing extracted tasks
        return False
    return False


def make_log_entry(action: str, details: Any) -> Dict[str, Any]:
    return {
        'time': datetime.now(timezone.utc).isoformat().replace(UTC_OFFSET, Z_SUFFIX),
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
            entry: Dict[str, Any] = {'iteration': iteration, 'time': datetime.now(timezone.utc).isoformat().replace(UTC_OFFSET, Z_SUFFIX), 'results': {}}
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
