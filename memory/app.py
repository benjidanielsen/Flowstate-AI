import os
from typing import List

import httpx
import numpy as np
from fastapi import FastAPI, Query
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity

EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

store: List[dict] = []
app = FastAPI()

async def embed(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
        )
        resp.raise_for_status()
        return resp.json().get("embedding", [])

class UpsertIn(BaseModel):
    text: str
    meta: dict

@app.post("/upsert")
async def upsert(payload: UpsertIn):
    vector = np.array(await embed(payload.text), dtype=np.float32)
    store.append({"v": vector, "m": payload.meta, "t": payload.text[:4000]})
    return {"count": len(store)}

@app.get("/search")
async def search(q: str = Query(...), k: int = 5):
    if not store:
        return []
    query_vec = np.array(await embed(q), dtype=np.float32).reshape(1, -1)
    matrix = np.stack([entry["v"] for entry in store])
    sims = cosine_similarity(query_vec, matrix).flatten()
    idx = np.argsort(-sims)[:k]
    results = []
    for i in idx:
        entry = store[i]
        results.append({
            "score": float(sims[i]),
            "meta": entry["m"],
            "text": entry["t"],
        })
    return results

@app.get("/")
async def root():
    return {"service": "memory", "count": len(store)}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
