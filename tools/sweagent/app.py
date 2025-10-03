import os
import subprocess
import tempfile
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

REPO_DIR = Path(os.getenv("REPO_DIR", "/workspace"))
DEFAULT_BRANCH = os.getenv("DEFAULT_BRANCH", "main")
OWNER = os.getenv("GITHUB_REPO_OWNER", "")
REPO = os.getenv("GITHUB_REPO_NAME", "")
TOKEN = os.getenv("GITHUB_TOKEN", "")
API = "https://api.github.com"

app = FastAPI()

class Patch(BaseModel):
    diff: str

class PRIn(BaseModel):
    title: str
    body: str | None = None
    branch: str = "godmode/auto"

@app.get("/")
async def root():
    return {"service": "sweagent", "repo": str(REPO_DIR)}

@app.post("/apply_patch")
async def apply_patch(payload: Patch):
    REPO_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
        tmp.write(payload.diff)
        patch_path = Path(tmp.name)
    try:
        subprocess.check_call(["git", "-C", str(REPO_DIR), "fetch", "--all"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass
    subprocess.check_call(["git", "-C", str(REPO_DIR), "checkout", DEFAULT_BRANCH])
    subprocess.check_call(["git", "-C", str(REPO_DIR), "checkout", "-B", "godmode/auto"])
    try:
        subprocess.check_call(["git", "-C", str(REPO_DIR), "apply", str(patch_path)])
    except subprocess.CalledProcessError:
        subprocess.check_call(["patch", "-p1", "-d", str(REPO_DIR), "-i", str(patch_path)])
    finally:
        patch_path.unlink(missing_ok=True)

    subprocess.check_call(["git", "-C", str(REPO_DIR), "add", "."])
    commit_rc = subprocess.call(["git", "-C", str(REPO_DIR), "commit", "-m", "[GODMODE] apply diff"], stdout=subprocess.DEVNULL)
    return {"ok": commit_rc == 0}

@app.post("/run_tests")
async def run_tests():
    command = os.getenv("TEST_COMMAND", "echo no tests")
    rc = subprocess.call(command, shell=True, cwd=REPO_DIR)
    return {"ok": rc == 0, "rc": rc}

@app.post("/open_pr")
async def open_pr(payload: PRIn):
    if not TOKEN:
        return {"ok": False, "error": "GITHUB_TOKEN missing"}
    subprocess.check_call(["git", "-C", str(REPO_DIR), "push", "-u", "origin", payload.branch])
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient(timeout=60, headers=headers) as client:
        url = f"{API}/repos/{OWNER}/{REPO}/pulls"
        resp = await client.post(
            url,
            json={
                "title": payload.title,
                "body": payload.body or "",
                "head": payload.branch,
                "base": DEFAULT_BRANCH,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return {"ok": True, "url": data.get("html_url"), "number": data.get("number")}
