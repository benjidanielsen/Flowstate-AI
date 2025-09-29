#!/usr/bin/env python3
"""Minimal safe scan script for .multicoder/task.

This lightweight shim finds markdown files in the repo root and writes a
basic `extracted_tasks.json` with summaries so the agent_runner can proceed.
It's intentionally conservative and safe to run in user workspaces.
"""
import os
import json
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.dirname(__file__)

def find_markdown(limit=20):
    results = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # skip .multicoder directory
        if '.multicoder' in dirpath.split(os.sep):
            continue
        for fn in filenames:
            if fn.lower().endswith('.md'):
                results.append(os.path.join(dirpath, fn))
                if len(results) >= limit:
                    return results
    return results

def summarize(path: str):
    try:
        with open(path, 'r', encoding='utf8') as f:
            txt = f.read()
    except Exception:
        return {'path': str(path), 'summary': ''}
    for line in txt.splitlines():
        s = line.strip()
        if s:
            return {'path': str(path), 'summary': s[:200]}
    return {'path': str(path), 'summary': ''}

def main():
    files = find_markdown()
    items = [summarize(p) for p in files]
    out_file = os.path.join(OUT, 'extracted_tasks.json')
    with open(out_file, 'w', encoding='utf8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    nt = os.path.join(OUT, 'next_tasks.md')
    with open(nt, 'w', encoding='utf8') as f:
        f.write('# Auto-extracted next tasks\n')
        for i, it in enumerate(items[:10], 1):
            f.write(f'{i}. {it.get("summary","(no summary)")}\n')
    # Use timezone-aware UTC timestamp to avoid deprecation warnings
    print(f'Wrote {out_file} with {len(items)} entries at {datetime.now(timezone.utc).isoformat()}')

if __name__ == '__main__':
    main()
