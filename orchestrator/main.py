import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from agents import evaluate, plan, solve
from github_client import create_issue, list_open_issues
from memory_client import embed_and_upsert, search
from tool_clients.swe_agent import apply_patch, open_pr, run_tests

load_dotenv()
app = FastAPI()

PAUSE_FILE = os.getenv("PAUSE_FILE", "/workspace/ops/PAUSE")
AUTOMERGE = os.getenv("AUTOMERGE", "false").lower() == "true"
THRESH = float(os.getenv("AUTOMERGE_SCORE_THRESHOLD", 0.78))
DEFAULT_BRANCH = os.getenv("DEFAULT_BRANCH", "main")

class Goal(BaseModel):
    text: str

@app.get("/")
def root():
    return {"service": "orchestrator", "paused": Path(PAUSE_FILE).exists()}

@app.post("/seed")
async def seed_repo_memory():
    indexed = 0
    workspace = Path("/workspace")
    for path in workspace.glob("**/*.md"):
        try:
            if path.stat().st_size > 200_000:
                continue
            snippet = path.read_text(errors="ignore")[:8000]
            await embed_and_upsert(snippet, {"path": str(path.relative_to(workspace))})
            indexed += 1
        except Exception:
            continue
        if indexed >= 100:
            break
    return {"indexed": indexed}

@app.post("/goals")
async def add_goal(goal: Goal):
    await embed_and_upsert(goal.text, {"type": "goal"})
    return await process_goal(goal.text)

@app.post("/pause")
async def pause():
    Path(PAUSE_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(PAUSE_FILE).write_text("paused")
    return {"paused": True}

@app.post("/resume")
async def resume():
    try:
        Path(PAUSE_FILE).unlink()
    except FileNotFoundError:
        pass
    return {"paused": False}

@app.post("/tick")
async def tick():
    if Path(PAUSE_FILE).exists():
        return {"status": "paused"}
    issues = await list_open_issues()
    if not issues:
        return {"status": "idle"}
    issue = issues[0]
    body = issue.get("body") or ""
    goal_text = f"{issue['title']}\n\n{body}"
    return await process_goal(goal_text)

async def process_goal(goal_text: str):
    if Path(PAUSE_FILE).exists():
        return {"status": "paused"}

    plan_obj = await plan(goal_text)
    branch = plan_obj.get("branch", "godmode/auto")
    tasks = plan_obj.get("tasks") or [{"file": "", "change_summary": goal_text}]

    context_hits = await search(goal_text, k=5)
    context_blob = json.dumps(context_hits)

    candidates: list[tuple[float, str]] = []
    for idx in range(2):
        task = tasks[min(idx, len(tasks) - 1)]
        diff = await solve(task.get("file", ""), task.get("change_summary", ""), context_blob)
        desc = (
            f"Candidate {idx} implements: {task.get('change_summary', '')}\n"
            f"Diff length: {len(diff)}"
        )
        score = await evaluate(desc)
        candidates.append((score, diff))

    candidates.sort(key=lambda item: item[0], reverse=True)
    best_score, best_diff = candidates[0]

    if best_score < 0.2:
        await create_issue("Goal blocked: low evaluation", f"{goal_text}\nScores={candidates}")
        return {"status": "blocked", "score": best_score}

    await apply_patch(best_diff)
    test_result = await run_tests()
    pr = await open_pr(
        title=f"[GODMODE] {goal_text[:50]}",
        body=f"Auto diff. Score={best_score}",
        branch=branch,
    )
    automerge = AUTOMERGE and best_score >= THRESH and test_result.get("ok", False)
    return {
        "score": best_score,
        "tests": test_result,
        "pr": pr,
        "automerge": automerge,
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("ORCH_PORT", 8088)))
