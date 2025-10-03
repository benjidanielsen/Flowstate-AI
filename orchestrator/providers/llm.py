import os
import httpx

PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

async def chat(messages: list[dict]) -> str:
    if PROVIDER == "ollama":
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{OLLAMA_HOST}/api/chat",
                json={"model": MODEL, "messages": messages, "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("message", {}).get("content", "")
    raise RuntimeError(f"Unsupported provider: {PROVIDER}")
