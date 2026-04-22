"""
gateway.py — Central API Gateway
Routes requests to challenges/<id>/agent.py

The evaluation engine POSTs:
  { "query": "...", "assets": ["url1", ...] }

We respond with:
  { "output": "..." }
"""

import importlib
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="LastCommit Agent Gateway")


class QueryPayload(BaseModel):
    query: str
    assets: list[str] = []


ACTIVE_CHALLENGE = os.environ.get("ACTIVE_CHALLENGE", "05")


# ── Health check ─────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok", "service": "LastCommit Agent Gateway"}


# ── Per-challenge routes ─────────────────────────────
# Each challenge gets its own clean endpoint.
# The evaluation engine hits the specific one you submit.

ACTIVE_CHALLENGES = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

@app.post("/v1/answer")
async def answer(payload: QueryPayload):
    """
    Default route used by the evaluation engine.
    Routes to the active challenge (set via env var, defaults to 05).
    """
    return await _dispatch(ACTIVE_CHALLENGE, payload)


async def _dispatch(challenge_id: str, payload: QueryPayload) -> JSONResponse:
    try:
        agent = importlib.import_module(f"challenges.{challenge_id}.agent")
    except ModuleNotFoundError:
        raise HTTPException(404, f"No agent for challenge {challenge_id!r}")

    try:
        result = agent.run(payload.query, payload.assets or None)
        if hasattr(result, "__await__"):
            result = await result
    except Exception as exc:
        raise HTTPException(500, str(exc))

    return JSONResponse(content={"output": result})


# Register a dedicated route for each challenge
for _cid in ACTIVE_CHALLENGES:
    # Closure to capture cid value
    def _make_handler(cid: str):
        async def handler(payload: QueryPayload):
            return await _dispatch(cid, payload)
        handler.__name__ = f"challenge_{cid}"
        return handler

    app.post(f"/challenge/{_cid}", name=f"challenge_{_cid}")(_make_handler(_cid))


# ── Fallback: generic route for any challenge ────────
@app.post("/challenge/{challenge_id}")
async def challenge_generic(challenge_id: str, payload: QueryPayload):
    return await _dispatch(challenge_id, payload)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("gateway:app", host="0.0.0.0", port=port, log_level=os.environ.get("LOG_LEVEL", "info"))
