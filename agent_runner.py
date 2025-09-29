#!/usr/bin/env python3
import argparse
import subprocess
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import sys

# Configuration paths
ROOT = Path(__file__).parent.absolute()
LOG_JSON = ROOT / 'logs' / 'agent_runner.json'
SCAN_PY = ROOT / 'scan.py'
SCAN_LOG = ROOT / 'logs' / 'scan.log'
TEST_LOG = ROOT / 'logs' / 'test.log'
EXTRACTED = ROOT / 'extracted_tasks.json'
NEXT_TASKS = ROOT / 'next_tasks.md'

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
            
            # Optional: run tests
            if args.run_tests:
                test_res = run_backend_tests()
                entry['results']['test'] = test_res
            
            # Update next tasks
            updated = update_next_tasks_from_extracted()
            entry['results']['next_tasks_updated'] = updated
            
            # Log the results
            append_log(entry)
            
            if args.once:
                break
                
            print(f'Iteration {iteration} complete. Sleeping {args.interval} seconds...')
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print('\nAgent runner interrupted by user (KeyboardInterrupt)')
    except Exception as e:
        append_log(make_log_entry('runner_exception', {'error': str(e)}))
        raise

if __name__ == '__main__':
    main()