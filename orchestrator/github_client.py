import os
import httpx

OWNER = os.getenv("GITHUB_REPO_OWNER", "")
REPO = os.getenv("GITHUB_REPO_NAME", "")
TOKEN = os.getenv("GITHUB_TOKEN", "")
API = "https://api.github.com"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"} if TOKEN else {}

async def list_open_issues():
    if not TOKEN:
        return []
    url = f"{API}/repos/{OWNER}/{REPO}/issues?state=open"
    async with httpx.AsyncClient(timeout=60, headers=HEADERS) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return [issue for issue in resp.json() if "pull_request" not in issue]

async def create_issue(title: str, body: str | None):
    if not TOKEN:
        return None
    url = f"{API}/repos/{OWNER}/{REPO}/issues"
    async with httpx.AsyncClient(timeout=60, headers=HEADERS) as client:
        resp = await client.post(url, json={"title": title, "body": body or ""})
        resp.raise_for_status()
        return resp.json()
