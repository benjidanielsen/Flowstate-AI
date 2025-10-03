# Flowstate-AI: Click and Play Setup Guide for VSCode

This guide provides a "click and play" experience for setting up and running the Flowstate-AI system within Visual Studio Code. Our goal is to minimize manual configuration and make the process as intuitive as possible.

## 1. Prerequisites: Install Essential Software

Before you begin, please ensure you have the following software installed on your **Windows**, Linux, or macOS system. If you already have them, you can skip ahead.

1.  **Git:** A version control system.
    *   Download: [https://git-scm.com/downloads](https://git-scm.com/downloads)
    *   Installation: Accept default options.

2.  **Python 3.11 (or newer):** The core language for Flowstate-AI.
    *   Download: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
    *   **CRITICAL:** During installation, check "**Add Python to PATH**" or "Add Python 3.x to PATH".

3.  **Node.js (LTS version):** For the dashboard frontend.
    *   Download: [https://nodejs.org/en/download/](https://nodejs.org/en/download/)
    *   Installation: Choose the LTS version and accept default options.

4.  **Visual Studio Code (VSCode):** Your development environment.
    *   Download: [https://code.visualstudio.com/download](https://code.visualstudio.com/download)
    *   Installation: Accept default options.

## 2. Get the Flowstate-AI Project

1.  **Open VSCode.**
2.  Go to `File > Open Folder...` (or `Ctrl+K Ctrl+O`).
3.  In the dialog box, paste the following GitHub repository URL and press Enter:
    ```
    https://github.com/benjidanielsen/Flowstate-AI.git
    ```
    *   Choose a location (e.g., `C:\Users\YourUser\Documents\Flowstate-AI`).
    *   VSCode will clone the repository and open the project.

## 3. Install Recommended VSCode Extensions

These extensions enhance your experience. Open the Extensions view (`Ctrl+Shift+X`), search for each, and click `Install`:

*   **Python** by Microsoft
*   **ESLint** by Microsoft
*   **Prettier - Code formatter** by Prettier

## 4. "Click and Play" Setup Automation

We've created a Python script to automate the setup of VSCode tasks. This script will:

*   Install necessary Python packages (`Flask`, `Gunicorn`, `Flask-SocketIO`).
*   Configure VSCode tasks for starting and stopping Flowstate-AI.

### Step 4.1: Run the Setup Script

1.  **Open the VSCode Terminal:** Go to `Terminal > New Terminal` (or `Ctrl+"`).
2.  **Copy and paste the following command into the terminal and press Enter:**

    ```bash
    # Navigate to the project root (if not already there)
    cd "${workspaceFolder}"

    # Install Python dependencies
    pip install Flask Gunicorn Flask-SocketIO

    # Run the Python script to create .vscode/tasks.json
    python3.11 create_vscode_tasks.py

    echo "Flowstate-AI setup complete! You can now run the system using VSCode tasks."
    ```

    *   **Explanation:** This script installs Python packages and creates the `.vscode/tasks.json` file directly within your project, configuring the "Start" and "Stop" tasks.

## 5. Run Flowstate-AI System

Now that the setup is complete, you can start the entire Flowstate-AI system with a single command in VSCode:

1.  Open the VSCode Command Palette (Ctrl+Shift+P or Cmd+Shift+P).
2.  Type `Tasks: Run Task` and press Enter.
3.  Select `Start Flowstate-AI System (Windows)` if you are on Windows, or `Start Flowstate-AI System (Linux/macOS)` if you are on Linux or macOS.

This will launch the Manus Sync Engine, Godmode Dashboard, Godmode Backend, and Godmode Frontend in the background.

## 6. Access the Dashboard

Once the system is running (after executing the "Start" task):

1.  Open your web browser (e.g., Chrome, Firefox, Edge).
2.  Navigate to: `http://localhost:3333`

You should now see the Flowstate-AI dashboard!

## 7. Stop Flowstate-AI System

To stop all running components of the Flowstate-AI system:

1.  Open the VSCode Command Palette (Ctrl+Shift+P or Cmd+Shift+P).
2.  Type `Tasks: Run Task` and press Enter.
3.  Select `Stop Flowstate-AI System (Windows)` or `Stop Flowstate-AI System (Linux/macOS)`.

## 8. Troubleshooting

*   **"Python not found"**: Ensure Python 3.11+ is installed and "Add Python to PATH" was checked during installation. Restart VSCode or your computer.
*   **"Address already in use"**: Another program is using port `3333`. Run the `Stop Flowstate-AI System (Windows)` task first. If it persists, restart your computer.
*   **Dashboard not loading**: Check the VSCode Terminal for errors. Ensure the "Start" task completed. Try `http://127.0.0.1:3333` or `http://169.254.0.21:3333`.

For further assistance, refer to `MANUS_KNOWLEDGE_BASE.md` and `COORDINATION_PROTOCOL.md` in the project repository.

