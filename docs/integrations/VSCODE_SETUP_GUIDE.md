# Flowstate-AI: "Click and Play" VSCode Setup Guide

Welcome to the Flowstate-AI project! This guide is designed to help you get the system up and running in Visual Studio Code with minimal effort, even if you're not familiar with VSCode or development environments.

Our goal is a "click and play" experience, so we've streamlined the setup as much as possible.

## 1. Prerequisites: What You Need Before You Start

Before diving into VSCode, please ensure you have the following software installed on your **Windows** computer:

1.  **Git:** A version control system to download and manage the project code.
    *   Download from: [https://git-scm.com/downloads](https://git-scm.com/downloads)
    *   During installation, you can generally accept the default options.

2.  **Python 3.11 (or newer):** The programming language for the Flowstate-AI backend and sync engine.
    *   Download from: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
    *   **IMPORTANT:** During installation, make sure to check the box that says "Add Python to PATH" or "Add Python 3.x to PATH". This is crucial for VSCode to find Python automatically.

3.  **Node.js (LTS version):** Required for the dashboard's frontend components.
    *   Download from: [https://nodejs.org/en/download/](https://nodejs.org/en/download/)
    *   Choose the LTS (Long Term Support) version. Accept default installation options.

4.  **Visual Studio Code (VSCode):** Your development environment.
    *   Download from: [https://code.visualstudio.com/download](https://code.visualstudio.com/download)
    *   Accept default installation options.

## 2. Getting the Flowstate-AI Project into VSCode

This section will guide you through cloning the project from GitHub and opening it in VSCode.

1.  **Open VSCode.**
2.  Go to `File > Open Folder...` (or `Ctrl+K Ctrl+O`).
3.  In the dialog box, paste the following GitHub repository URL and press Enter:
    ```
    https://github.com/benjidanielsen/Flowstate-AI.git
    ```
    *   If prompted, choose a location on your computer where you want to save the project (e.g., `C:\Users\YourUser\Documents\Flowstate-AI`).
    *   VSCode will then clone the repository and open the project folder.

## 3. Recommended VSCode Extensions

VSCode extensions enhance your development experience. We recommend installing the following:

1.  **Python:** Provides rich support for Python development.
    *   Open the Extensions view (`Ctrl+Shift+X`).
    *   Search for `Python` by Microsoft.
    *   Click `Install`.

2.  **ESLint:** For JavaScript/TypeScript linting (code quality).
    *   Open the Extensions view (`Ctrl+Shift+X`).
    *   Search for `ESLint` by Microsoft.
    *   Click `Install`.

3.  **Prettier - Code formatter:** Automatically formats your code for consistency.
    *   Open the Extensions view (`Ctrl+Shift+X`).
    *   Search for `Prettier - Code formatter` by Prettier.
    *   Click `Install`.

## 4. "Click and Play" with VSCode Tasks

We've configured VSCode tasks to make starting the Flowstate-AI system as simple as possible.

1.  **Open the Command Palette:** Press `Ctrl+Shift+P`.
2.  Type `Tasks: Run Task` and select it.
3.  You will see a list of predefined tasks. Select the following:
    *   `Start Flowstate-AI System (Windows)`: This task will launch the entire Flowstate-AI system, including the enhanced sync engine and the dashboard.

    *   **What happens when you run this task?**
        *   It will automatically start the `MANUS_SYNC_ENGINE_ENHANCED.py` in the background.
        *   It will then start the enhanced dashboard (`app_enhanced.py`) using Gunicorn (a production-ready server) on `http://localhost:3333`.
        *   You should see output in the VSCode Terminal indicating that both components are starting.

## 5. Accessing the Dashboard

Once the `Start Flowstate-AI System (Windows)` task is running:

1.  Open your web browser (e.g., Chrome, Firefox, Edge).
2.  Navigate to: `http://localhost:3333`

You should now see the Flowstate-AI dashboard, displaying the status of your AI agents!

## 6. Stopping the Flowstate-AI System

To stop all running Flowstate-AI components:

1.  **Open the Command Palette:** Press `Ctrl+Shift+P`.
2.  Type `Tasks: Run Task` and select it.
3.  Select:
    *   `Stop Flowstate-AI System (Windows)`: This task will gracefully shut down all running Flowstate-AI processes.

## 7. Troubleshooting Common Issues

*   **"Python not found" or similar errors:** Ensure Python is correctly installed and "Add Python to PATH" was selected during installation. You might need to restart VSCode or your computer after installing Python.
*   **"Address already in use" errors:** This means another program is using port `3333`. Run the `Stop Flowstate-AI System (Windows)` task first, then try starting again. If the issue persists, restart your computer.
*   **Dashboard not loading in browser:** Check the VSCode Terminal for any error messages. Ensure the `Start Flowstate-AI System (Windows)` task completed successfully. If you are still having issues, try accessing `http://127.0.0.1:3333` or `http://169.254.0.21:3333` (though `localhost` should work).

If you encounter any persistent issues, please refer to the `MANUS_KNOWLEDGE_BASE.md` and `COORDINATION_PROTOCOL.md` files in the project repository, or reach out for further assistance. We are committed to making this a seamless experience for you!
