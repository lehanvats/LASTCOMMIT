# Project Context: Cherry+ Network "The Last Commit" Hackathon
**Event Date:** April 22, 2026 | **Event Mode:** In-Person (TP2 1220)

## 🎯 The Objective
We are building an **Autonomous Agentic API** that acts, plans, and delivers entirely on its own. We are not solving prompts manually. Our system will receive a webhook request with a query and context URLs, and it must autonomously return the correct answer.

## ⚙️ The Tech Stack
*   **Backend:** Python + FastAPI
*   **LLM Provider:** Groq SDK — model: `openai/gpt-oss-120b`
*   **Exposure:** Render (hosted Web Service — always-on, public HTTPS URL exposed to the Hackathon Evaluation Engine)

## 📏 Core Rules & Constraints
*   **Time Limit:** 20,000ms (20 seconds) hard limit per request. 
*   **Attempts:** Max 3 attempts allowed per 20-minute window for each level.
*   **Progression:** Upon passing a level, the 20-minute timer instantly resets for the next level.
*   **Scoring:** Evaluated purely on Cosine Similarity and n-gram Jaccard scoring against the hidden expected output.

## 📡 API Payload Architecture
**Endpoint:** `POST /v1/answer`

**Incoming Request Format:**
```json
{
  "query": "The question or problem statement as a string",
  "assets": ["https://asset-url-1.com", "https://asset-url-2.com"] // Optional context links
}
```

**Expected Response Format:**
```json
{
  "output": "The precise answer to the query without conversational filler"
}
```

## 📈 Progressive Level Roadmap (1 to 40)
Our AI agent needs dynamic routing to evolve through these checkpoint problem types:
1.  **Level 1-4:** Basic formatting (Valid JSON), Entity Extraction, Summarization, Structured Data Processing.
2.  **Level 5-6:** Solving coding problems & Handling ambiguous, tricky inputs.
3.  **Level 7:** RAG (Retrieval-Augmented Generation) — Answering purely from the provided `assets` URLs.
4.  **Level 8-9:** Optimizing for extreme latency & Detecting data anomalies.
5.  **Level 10+:** Performing complex multi-step reasoning chains & Handling incomplete data.

## 🗂️ Project Structure
```
gateway.py                  ← FastAPI entry-point; routes POST /challenge/{id} to the right agent
challenges/
  01/
  │   agent.py             ← ReAct / tool-calling agent for this level (uses Groq)
  │   api.py               ← all outbound HTTP: fetch challenge input, submit answer
  │   __init__.py
  02/ … 12/                ← same layout repeated per level
requirements.txt
.env.example
.gitignore
```

## 🤖 AI Assistant Instructions (For Teammates' AIs)
If you are an AI reading this file:
1.  Prioritize **low-latency** and **deterministic** code.
2.  Do not include conversational filler in the LLM system prompts.
3.  Each challenge lives in `challenges/<id>/`. The agent logic goes in `agent.py`; all HTTP calls (fetch input, submit output, hit external tools) go in `api.py`. Keep them separate.
4.  `gateway.py` dynamically imports `challenges.{id}.agent` and calls it — one isolated agent instance per request.
5.  Always ensure the output JSON matches `{"output": "result"}` perfectly.
6.  The Groq model is `openai/gpt-oss-120b`. Read `GROQ_API_KEY` from the environment — never hardcode it.
