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
import json
import re
import glob

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="LastCommit Agent Gateway")

def fix_payload(s: str) -> str:
    match_start = re.search(r'"query"\s*:\s*"', s)
    if not match_start:
        return s
    start_idx = match_start.end()
    
    if '"assets"' in s[start_idx:]:
        match_end = re.search(r'"\s*,\s*"assets"', s[start_idx:])
        if match_end:
            end_idx = start_idx + match_end.start()
            query_val = s[start_idx:end_idx]
            query_val = query_val.replace('\\"', '"').replace('"', '\\"')
            return s[:start_idx] + query_val + s[end_idx:]
            
    match_end = re.search(r'"\s*}', s[start_idx:])
    if match_end:
        last_brace = s.rfind('}')
        if last_brace != -1:
            last_quote = s.rfind('"', start_idx, last_brace)
            # Make sure there are only spaces between last_quote and last_brace
            if s[last_quote+1:last_brace].strip() == '':
                query_val = s[start_idx:last_quote]
                query_val = query_val.replace('\\"', '"').replace('"', '\\"')
                return s[:start_idx] + query_val + s[last_quote:]
                
    return s

@app.middleware("http")
async def fix_malformed_json(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()
        if body:
            body_str = body.decode("utf-8")
            try:
                json.loads(body_str)
                # It's valid, restore body
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            except json.JSONDecodeError:
                fixed_body_str = fix_payload(body_str)
                try:
                    json.loads(fixed_body_str)
                    async def receive():
                        return {"type": "http.request", "body": fixed_body_str.encode("utf-8")}
                    request._receive = receive
                except json.JSONDecodeError:
                    async def receive():
                        return {"type": "http.request", "body": body}
                    request._receive = receive
    return await call_next(request)


class QueryPayload(BaseModel):
    query: str
    assets: list[str] = []

def get_active_challenge() -> str:
    # Intuitively find the highest numbered challenge that has been implemented
    agents = sorted(glob.glob("challenges/*/agent.py"), reverse=True)
    for agent_file in agents:
        with open(agent_file, "r", encoding="utf-8") as f:
            if "def run(" in f.read():
                return os.path.basename(os.path.dirname(agent_file))
    return "01"

ACTIVE_CHALLENGE = os.environ.get("ACTIVE_CHALLENGE") or get_active_challenge()


# ── Health check ─────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok", "service": "LastCommit Agent Gateway"}


# ── Per-challenge routes ─────────────────────────────
# Each challenge gets its own clean endpoint.
# The evaluation engine hits the specific one you submit.

ACTIVE_CHALLENGES = [f"{i:02d}" for i in range(1, 26)]

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
        print(f"[{challenge_id}] INPUT: {payload.query}  =>  OUTPUT: {result}", flush=True)
    except Exception as exc:
        print(f"[{challenge_id}] ERROR: {str(exc)}", flush=True)
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
