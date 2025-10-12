# VS Code Setup Guide for Flowstate-AI Development

This guide provides recommendations and steps for setting up Visual Studio Code for Flowstate-AI development, ensuring a consistent and productive environment across the team.

## 1. Recommended VS Code Extensions

Install the following extensions for an optimal development experience:

- **ESLint**: Integrates ESLint into VS Code, providing real-time feedback on code quality and style.
  - `dbaeumer.vscode-eslint`
- **Prettier - Code formatter**: Formats your code consistently.
  - `esbenp.prettier-vscode`
- **TypeScript and JavaScript Language Features**: Built-in, but ensure it's up-to-date.
- **Docker**: Adds Docker file and image management, and Docker Compose integration.
  - `ms-azuretools.vscode-docker`
- **Python**: Rich support for Python development, including linting, debugging, and IntelliSense.
  - `ms-python.python`
- **Tailwind CSS IntelliSense**: Provides advanced features like autocomplete, syntax highlighting, and linting for Tailwind CSS.
  - `bradlc.vscode-tailwindcss`
- **Markdown All in One**: Provides full Markdown support (keyboard shortcuts, table of contents, auto preview, etc.).
  - `yzhang.markdown-all-in-one`
- **YAML**: YAML language support with auto-completion and syntax highlighting.
  - `redhat.vscode-yaml`

## 2. VS Code Settings Recommendations

To ensure consistent formatting and linting, add or update the following settings in your `.vscode/settings.json` file (create if it doesn't exist):

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "eslint.format.enable": true,
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "python.linting.pylintEnabled": true,
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "python.terminal.activateEnvironment": true,
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  },
  "files.eol": "\n", // Ensure LF line endings for cross-platform consistency
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true
}
```

## 3. Local Development Environment Setup

Follow the `Quick Start` section in the main `README.md` for setting up your local development environment, including cloning the repository, installing dependencies, and initializing the database.

### Python Virtual Environment

It is highly recommended to use a Python virtual environment for the `python-worker` and `ai-gods` components.

1.  Navigate to the `python-worker` directory:
    ```bash
    cd python-worker
    ```
2.  Create a virtual environment:
    ```bash
    python3 -m venv .venv
    ```
3.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
    (On Windows, use `.venv\Scripts\activate`)
4.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  In VS Code, select the interpreter from your virtual environment (`.venv/bin/python`).

Repeat similar steps for `ai-gods` if it has its own `requirements.txt` or specific dependencies.

## 4. Git Configuration

Ensure your Git client is configured with your user name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 5. Troubleshooting

- **Linting/Formatting issues**: Ensure ESLint and Prettier extensions are enabled and configured to format on save. Check VS Code output panels for errors.
- **TypeScript errors**: Run `npm run build:frontend` or `npm run build:backend` in the respective directories to get detailed compilation errors.
- **Python environment**: Ensure your virtual environment is activated and selected in VS Code.

By following this guide, you should have a robust and consistent development environment for Flowstate-AI.
