'''
import os
import json

tasks = {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Flowstate-AI System (Windows)",
            "type": "shell",
            "command": "Start-Process python -ArgumentList \"./MANUS_SYNC_ENGINE_ENHANCED.py\" -NoNewWindow; Start-Process python -ArgumentList \"./godmode-dashboard/app_enhanced.py\" -NoNewWindow; Start-Process python -ArgumentList \"./godmode-backend/backend.py\" -NoNewWindow; Start-Process node -ArgumentList \"./godmode-frontend/server.js\" -NoNewWindow",
            "windows": {
                "command": "Start-Process python -ArgumentList \"./MANUS_SYNC_ENGINE_ENHANCED.py\" -NoNewWindow; Start-Process python -ArgumentList \"./godmode-dashboard/app_enhanced.py\" -NoNewWindow; Start-Process python -ArgumentList \"./godmode-backend/backend.py\" -NoNewWindow; Start-Process node -ArgumentList \"./godmode-frontend/server.js\" -NoNewWindow"
            },
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Stop Flowstate-AI System (Windows)",
            "type": "shell",
            "command": "Stop-Process -Name python; Stop-Process -Name node",
            "windows": {
                "command": "Stop-Process -Name python; Stop-Process -Name node"
            },
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        }
    ]
}

if not os.path.exists(".vscode"):
    os.makedirs(".vscode")

with open(".vscode/tasks.json", "w") as f:
    json.dump(tasks, f, indent=4)

print("✅ VSCode tasks.json file created successfully.")
'''
