"""
Challenge 01 — Agent
Level 1: Basic formatting / arithmetic queries.
Receives a query (and optional asset URLs) and uses Groq to produce
a terse, correctly-formatted answer that maximises cosine similarity
against the evaluation engine's expected output.
"""

import os
from groq import Groq

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


SYSTEM_PROMPT = """\
You are a precise answer engine. Your ONLY job is to produce the shortest \
correct answer in the exact format requested.

STRICT RULES — follow every one without exception:
1. For arithmetic questions (addition, subtraction, multiplication, division, \
   modulo, exponentiation):
   - Respond EXACTLY as: "The <operation_word> is <result>."
   - operation_word mapping:
       +  → sum
       -  → difference
       *  → product
       /  → quotient
       %  → remainder
       ** → result
   - Example: "What is 10 + 15?" → "The sum is 25."
   - Example: "What is 8 * 7?"   → "The product is 56."
   - Example: "What is 20 - 3?"  → "The difference is 17."
2. For factual / knowledge questions: respond in ONE concise sentence, \
   no filler, no preamble, no explanation.
3. For yes/no questions: answer only "Yes." or "No." followed by one \
   short justification sentence if needed.
4. NEVER include phrases like "Sure!", "Of course!", "Certainly!", \
   "I think", "Please note", or any conversational filler.
5. NEVER repeat the question.
6. NEVER add markdown, bullet points, headers, or code blocks unless \
   the question explicitly asks for them.
7. Output plain text only — the exact string that will be compared \
   character-by-character for scoring.
"""


def run(query: str, assets: list[str] | None = None) -> str:
    """
    Entry-point called by gateway.py.

    Parameters
    ----------
    query  : The question / problem statement.
    assets : Optional list of context URLs (ignored at Level 1).

    Returns
    -------
    The answer string (NOT wrapped in JSON — gateway handles that).
    """
    client = _get_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=messages,
        temperature=0.0,   # fully deterministic
        max_tokens=128,    # level 1 answers are always short
    )

    answer = response.choices[0].message.content.strip()
    return answer
