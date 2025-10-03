import json
import re
from typing import Dict, List

from providers import llm

SYSTEM_PM = (
    "You are the Project Manager AI. Break goals into steps and a branch plan. "
    "Return JSON: {\"plan\":[steps], \"branch\":\"branch-name\", "
    "\"tasks\":[{\"file\":\"\",\"change_summary\":\"\"}]}"
)
SYSTEM_SOLVER = "You are a senior engineer. Output ONLY unified diff (git patch). No prose."
SYSTEM_EVAL = "Return ONLY a float score 0..1 judging safety/testability/clarity of candidate."

def _coerce_json(raw: str) -> Dict:
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return {"plan": [], "branch": "godmode/auto", "tasks": []}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"plan": [], "branch": "godmode/auto", "tasks": []}

async def plan(goal: str) -> Dict:
    response = await llm.chat([
        {"role": "system", "content": SYSTEM_PM},
        {"role": "user", "content": goal},
    ])
    payload = _coerce_json(response)
    if not payload.get("tasks"):
        payload["tasks"] = [{"file": "", "change_summary": goal}]
    payload.setdefault("branch", "godmode/auto")
    return payload

async def solve(file_hint: str, change_summary: str, context: str) -> str:
    prompt = (
        f"Implement: {change_summary}\nFile hint: {file_hint}\nContext:\n{context}\n"
        "Return unified diff only."
    )
    return await llm.chat([
        {"role": "system", "content": SYSTEM_SOLVER},
        {"role": "user", "content": prompt},
    ])

async def evaluate(description: str) -> float:
    try:
        score = await llm.chat([
            {"role": "system", "content": SYSTEM_EVAL},
            {"role": "user", "content": description},
        ])
        return max(0.0, min(1.0, float(score.strip())))
    except Exception:
        return 0.0
