import os
import httpx

MEMORY_URL = os.getenv("MEMORY_URL", "http://memory:8080")

async def embed_and_upsert(text: str, meta: dict):
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{MEMORY_URL}/upsert", json={"text": text, "meta": meta})
        resp.raise_for_status()
        return resp.json()

async def search(query: str, k: int = 5):
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(f"{MEMORY_URL}/search", params={"q": query, "k": k})
        resp.raise_for_status()
        return resp.json()
