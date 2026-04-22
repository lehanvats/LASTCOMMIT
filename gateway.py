"""
gateway.py — Central API Gateway
POST /v1/answer  →  routes to challenges/<id>/agent.py based on level.

The evaluation engine POSTs:
  { "query": "...", "assets": ["url1", ...] }

We respond with:
  { "output": "..." }
"""

import importlib
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="LastCommit Agent Gateway")


class QueryPayload(BaseModel):
    query: str
    assets: list[str] = []


@app.post("/v1/answer")
async def answer(payload: QueryPayload):
    """
    Default route used by the evaluation engine.
    Routes to challenge 01 agent (the active level).
    """
    return await _dispatch("01", payload)


@app.post("/challenge/{challenge_id}")
async def challenge_route(challenge_id: str, payload: QueryPayload):
    """
    Internal / debug route to target a specific challenge directly.
    """
    return await _dispatch(challenge_id, payload)


async def _dispatch(challenge_id: str, payload: QueryPayload) -> JSONResponse:
    module_path = f"challenges.{challenge_id}.agent"
    try:
        agent = importlib.import_module(module_path)
    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail=f"No agent found for challenge {challenge_id!r}")

    try:
        result = agent.run(payload.query, payload.assets or None)
        # Support both sync and async agents
        if hasattr(result, "__await__"):
            result = await result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse(content={"output": result})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "gateway:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 8000)),
        log_level=os.environ.get("LOG_LEVEL", "info"),
    )
