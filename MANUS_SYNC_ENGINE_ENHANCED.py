#!/usr/bin/env python3
"""Enhanced Manus Sync Engine launcher.

This wrapper ensures the GODMODE orchestrator v2 boots cleanly on Windows by
creating required directories, wiring logging, and delegating to the
`GODMODEOrchestratorV2` runtime.  It keeps backwards compatibility with legacy
startup scripts that still invoke `MANUS_SYNC_ENGINE_ENHANCED.py` while the
modern orchestration logic lives in `ai_gods/godmode_orchestrator_v2.py`.
"""

from __future__ import annotations

import asyncio
import signal
import sys
from pathlib import Path
import io

# Force UTF-8 encoding for stdout and stderr on Windows.
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def _prepare_environment() -> None:
    """Prepare paths and logging directories before importing orchestrator."""
    project_root = Path(__file__).parent.resolve()
    log_dir = project_root / "godmode-logs"
    log_dir.mkdir(exist_ok=True)

    ai_gods_dir = project_root / "ai_gods"
    if str(ai_gods_dir) not in sys.path:
        sys.path.insert(0, str(ai_gods_dir))


_prepare_environment()

# Import after environment is prepared so logging file handlers can be created.
from godmode_orchestrator_v2 import GODMODEOrchestratorV2  # noqa: E402


async def _run_orchestrator() -> None:
    orchestrator = GODMODEOrchestratorV2()

    # Install signal handlers to support graceful shutdown (ctrl+c / taskkill).
    signal.signal(signal.SIGINT, orchestrator.signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, orchestrator.signal_handler)

    await orchestrator.run()


def main() -> None:
    try:
        asyncio.run(_run_orchestrator())
    except KeyboardInterrupt:
        # Allow clean shutdown without noisy stack traces.
        pass


if __name__ == "__main__":
    main()

