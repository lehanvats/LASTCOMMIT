# LASTCOMMIT — Agentic AI Hackathon

## Structure
```
gateway.py              ← single entry-point; routes each challenge URL to the right agent
challenges/
  01/ … 12/            ← one sub-dir per challenge level
    agent.py           ← ReAct / tool-calling agent for this level
    api.py             ← all HTTP calls (fetch input, submit output, any tools)
requirements.txt
.env.example
.gitignore
```

## Quick start
```bash
cp .env.example .env   # add your GROQ_API_KEY
pip install -r requirements.txt
uvicorn gateway:app --reload
```

## Endpoints
`POST /challenge/{id}` — runs the agent for challenge level `{id}` (1-12)
