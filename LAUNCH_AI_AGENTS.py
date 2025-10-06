#!/usr/bin/env python3
"""
🚀 THIS SCRIPT IS DEPRECATED
The system has been upgraded to use a consolidated orchestrator.
"""

import logging
import sys
from pathlib import Path

# Setup basic logging to inform the user
log_dir = Path(__file__).parent / "godmode-logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="🚀 [AI-LAUNCHER-DEPRECATED] %(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "ai-launcher.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    """
    This script is deprecated. The new entry point is ai_gods.godmode_orchestrator_v2.
    Please run `python -m ai_gods.godmode_orchestrator_v2`
    """
    logger.warning("=" * 80)
    logger.warning("⚠️  DEPRECATION WARNING: LAUNCH_AI_AGENTS.py is no longer used.")
    logger.warning("The system now uses a consolidated orchestrator.")
    logger.warning("Please run the new entry point:")
    logger.warning("  python -m ai_gods.godmode_orchestrator_v2")
    logger.warning("This script will now exit.")
    logger.warning("=" * 80)
    sys.exit(0)


if __name__ == "__main__":
    main()
