# VSCode Guide for FlowState-AI with GODMODE System

This guide will help you set up your Visual Studio Code (VSCode) environment to work seamlessly with the FlowState-AI project, especially with the new GODMODE AI system.

## 🚀 Quick Setup

1.  **Clone the Repository:**
    If you haven't already, clone the FlowState-AI repository to your local machine:
    ```bash
    git clone https://github.com/benjidanielsen/Flowstate-AI.git
    cd Flowstate-AI
    ```

2.  **Open in VSCode:**
    Open the cloned `Flowstate-AI` folder in VSCode.

3.  **Install Recommended Extensions:**
    VSCode will likely recommend some extensions based on the project's file types (Python, JavaScript/TypeScript). Install them. Key extensions include:
    *   **Python** (Microsoft): For Python language support, debugging, and linting.
    *   **ESLint** (Dirk Baeumer): Integrates ESLint into VSCode.
    *   **Prettier - Code formatter** (Prettier): For consistent code formatting.
    *   **TypeScript and JavaScript Language Features** (Microsoft): Usually built-in, but ensure it's active.
    *   **GitHub Copilot** (GitHub): For AI-powered code suggestions (if you have access).

4.  **Start the GODMODE System:**
    Open the integrated terminal in VSCode (`Ctrl+\` or `Cmd+\`).

    **On Windows:**
    ```cmd
    # Using Command Prompt
    godmode_start.bat
    
    # Or using PowerShell
    .\godmode_start.ps1
    ```

    **On Linux/macOS:**
    ```bash
    python3 godmode_start.py
    ```

    **Important Note on Proactive Local Environment Maintenance:** The `godmode_start.py` (and its Windows counterparts) now initiates **proactive local environment maintenance**. This means that during startup, the Fixer AI, coordinated by the Project Manager, will automatically:
    *   Check for and install missing Python dependencies (like `psutil`).
    *   Check for and install missing Node.js `node_modules` in both `backend` and `frontend` directories.
    *   Run necessary database migrations (`npm run db:migrate`).

    This significantly reduces manual setup and troubleshooting, allowing the AI agents to ensure a smooth operating environment from the outset.

## 📊 Monitoring AI Agents in VSCode

While the primary GODMODE Dashboard is accessible via your web browser (http://localhost:3333), you can also monitor AI agent activities and logs directly within VSCode:

1.  **Integrated Terminal:** The `godmode_start.py` script will output logs from the Project Manager and other agents directly to your VSCode terminal. Keep an eye on this for real-time updates.

2.  **`godmode-logs/` Directory:** Explore the `godmode-logs/` directory in your VSCode file explorer. Each AI agent (e.g., `project-manager.log`, `fixer-ai.log`) will have its own log file, providing detailed insights into their operations, decisions, and any issues encountered.

3.  **AI Chat Interface:** Access the AI Chat at `http://localhost:3333/chat` in your browser to directly communicate with the AI agents and query their status or progress.

## 💡 Tips for Working with GODMODE AI

*   **Observe and Learn:** The AI agents are designed to be autonomous. Observe their logs and the dashboard to understand their workflow and decision-making processes.
*   **Provide Feedback (via Chat/Issues):** If you notice any issues or have suggestions, use the AI Chat interface or open a GitHub issue. The Support AI and Innovation AI are designed to process this feedback.
*   **Review Code Changes:** The AI agents will be making changes to the codebase. Regularly review `git status` and `git log` to see their contributions. The DevOps AI handles commits and pushes.
*   **Leverage VSCode Features:** Use VSCode's powerful search, linting, and debugging features to navigate and understand the code generated and managed by the AI agents.

## Troubleshooting within VSCode

*   **Terminal Output:** Always check the VSCode terminal output for errors when starting the system. The proactive maintenance should catch many issues, but any remaining errors will be logged here.
*   **Log Files:** For deeper diagnostics, examine the specific agent log files in `godmode-logs/`.
*   **Restart VSCode:** Sometimes, simply restarting VSCode can resolve environment path issues or extension conflicts.
*   **Check `godmode_start.py`:** If the system fails to start, review `godmode_start.py` for any errors or unexpected behavior, especially if you've made modifications.

This guide will be continuously updated by the Documentation AI as the GODMODE system evolves. Happy coding with your autonomous AI team!
