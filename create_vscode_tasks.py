import json
import os

tasks = {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Fix Code Style Issues",
            "type": "npm",
            "script": "lint:fix",
            "detail": "Runs the 'lint:fix' script from package.json (e.g., eslint --fix .)",
            "group": "none",
        },
        {
            "label": "Scan for Issues",
            "type": "npm",
            "script": "lint",
            "detail": "Runs the 'lint' script from package.json (e.g., eslint .)",
            "group": "test",
        },
        {
            "label": "Start Flowstate-AI System",
            "group": {"kind": "build", "isDefault": True},
            "runOptions": {"runOn": "folderOpen"},
            "command": "powershell",
            "args": [
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "${workspaceFolder}/scripts/windows/START_FLOWSTATE_WINDOWS.ps1",
            ],
        },
        {
            "label": "Stop Flowstate-AI System",
            "type": "process",
            "command": "powershell",
            "group": "none",
            "args": [
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "${workspaceFolder}/scripts/windows/STOP_FLOWSTATE_WINDOWS.ps1",
            ],
        },
        {
            "label": "Restart Flowstate-AI System",
            "dependsOn": ["Stop Flowstate-AI System", "Start Flowstate-AI System"],
            "dependsOrder": "sequence",
            "group": {"kind": "test", "isDefault": True},
        },
    ],
}

if not os.path.exists(".vscode"):
    os.makedirs(".vscode")

with open(".vscode/tasks.json", "w") as f:
    json.dump(tasks, f, indent=4)

print("✅ VSCode tasks.json file created successfully.")
