# SANDBOX ACCESS INSTRUCTIONS - MANUS #3

This document provides instructions for accessing and utilizing the current sandbox environment of Manus #3 for coordinated development on the Flowstate-AI project.

## Current Sandbox Environment Details

*   **Operating System:** Ubuntu 22.04 Linux/amd64
*   **Python Version:** 3.11.0rc1
*   **Node.js Version:** 22.13.0
*   **Pre-installed Tools:** `gh` (GitHub CLI), `curl`, `pip`, `npm`, `manus-mcp-cli`, etc.
*   **Project Root:** `/home/ubuntu/Flowstate-AI_user/` (This is where the cloned `Flowstate-AI` repository resides)
*   **Dashboard URL:** `http://localhost:3333` (The enhanced dashboard is running here)
*   **Sync Engine:** `MANUS_SYNC_ENGINE_ENHANCED.py` is located at `/home/ubuntu/Flowstate-AI_user/MANUS_SYNC_ENGINE_ENHANCED.py`
*   **Dashboard Application:** `app_enhanced.py` is located at `/home/ubuntu/Flowstate-AI_user/godmode-dashboard/app_enhanced.py`

## How to Access and Use This Sandbox

To connect to and work within this sandbox environment, the user (or another Manus instance) will typically interact through the platform's provided interface. This interface allows for:

1.  **Shell Access:** Direct command-line access to the Ubuntu environment.
2.  **File System Access:** Ability to read, write, and modify files within the `/home/ubuntu/` directory.
3.  **Browser Access:** Interaction with web applications running within the sandbox (e.g., `http://localhost:3333`).

### Key Files and Their Locations

*   **Enhanced Sync Engine:** `/home/ubuntu/Flowstate-AI_user/MANUS_SYNC_ENGINE_ENHANCED.py`
*   **Enhanced Dashboard App:** `/home/ubuntu/Flowstate-AI_user/godmode-dashboard/app_enhanced.py`
*   **Windows Compatibility Test Script:** `/home/ubuntu/Flowstate-AI_user/test_windows_compatibility.py`
*   **Coordination Status File:** `/home/ubuntu/Flowstate-AI_user/.manus-coordination/coordination-status.json`
*   **Coordination Plan (Manus #3):** `/home/ubuntu/Flowstate-AI_user/COORDINATION_PLAN_MANUS_3.md`

### Running the Flowstate-AI System Components

To run the enhanced Flowstate-AI system components within this sandbox:

1.  **Start the Enhanced Sync Engine:**
    ```bash
    cd /home/ubuntu/Flowstate-AI_user
    python3.11 MANUS_SYNC_ENGINE_ENHANCED.py
    ```
    *Note: This will start the sync engine in the background. You may want to run it in a separate shell session or use a process manager for continuous operation.*

2.  **Start the Enhanced Dashboard:**
    ```bash
    cd /home/ubuntu/Flowstate-AI_user/godmode-dashboard
    python3.11 app_enhanced.py
    ```
    *The dashboard will be accessible via the sandbox browser at `http://localhost:3333`.*

### GitHub Integration

The `Flowstate-AI` repository has been cloned to `/home/ubuntu/Flowstate-AI_user/`. All changes made by Manus #3 have been committed and pushed to the `main` branch of this repository. Other Manus instances should clone this repository and pull the latest changes to synchronize their work.

### Autonomous Coordination

All coordination will be managed through the `.manus-coordination/coordination-status.json` file. Please ensure to:

*   **Pull Latest Changes:** Before starting any work, pull the latest changes from the `main` branch to get the most up-to-date `coordination-status.json`.
*   **Update Status:** Update your entry in `coordination-status.json` every 30 minutes with your current task, progress, and any completed work or blocking issues.
*   **Push Changes:** Commit and push your updated `coordination-status.json` to the `main` branch.

Manus #3 is ready for autonomous, direct Manus-to-Manus coordination.
