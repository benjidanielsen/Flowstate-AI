import os
import httpx

SWE_URL = os.getenv("SWEAGENT_URL", "http://sweagent:8086")

async def apply_patch(diff: str):
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(f"{SWE_URL}/apply_patch", json={"diff": diff})
        resp.raise_for_status()
        return resp.json()

async def run_tests():
    async with httpx.AsyncClient(timeout=900) as client:
        resp = await client.post(f"{SWE_URL}/run_tests")
        resp.raise_for_status()
        return resp.json()

async def open_pr(title: str, body: str, branch: str):
    async with httpx.AsyncClient(timeout=120) as client:
        payload = {"title": title, "body": body, "branch": branch}
        resp = await client.post(f"{SWE_URL}/open_pr", json=payload)
        resp.raise_for_status()
        return resp.json()
