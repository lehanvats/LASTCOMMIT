"""
Challenge 01 — Agent
Level 1: Basic formatting / general queries.

Strategy: Minimal rule-based prompt — no few-shot examples, no token cap.
The model reads the question's tone and matches answer length accordingly.
"""

import os
import re
from groq import Groq

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


SYSTEM_PROMPT = """\
You are a precise answer engine. Your job is to answer questions directly \
and correctly, matching the tone and expected length of the question.

RULES:
1. Match the question's implied format and length:
   - A direct one-word question gets a direct one-word answer.
   - A question asking you to list or recite something gets a full list.
   - An arithmetic question (add, subtract, multiply, divide, etc.) answers \
     as a complete sentence: "The <operation_noun> is <value>." \
     where operation_noun is: addition→sum, subtraction→difference, \
     multiplication→product, division→quotient, modulo→remainder.
2. Never use conversational filler: no "Sure!", "Of course!", "Certainly!", \
   "I think", "Here is", "Great question", or any similar phrases.
3. Never repeat or rephrase the question in your answer.
4. Do not add explanations, caveats, or extra commentary unless the question \
   explicitly asks for them.
5. Match punctuation intuitively — use whatever punctuation a clean, \
   professional answer would naturally have for that question type.
6. Output plain text only. No markdown, no bullet points, no headers, unless \
   the question explicitly asks for a structured format.
"""


def _clean(text: str) -> str:
    """Strip accidental leading 'A:' prefix the model may echo."""
    text = text.strip()
    text = re.sub(r"^A:\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def run(query: str, assets: list[str] | None = None) -> str:
    """
    Entry-point called by gateway.py.

    Parameters
    ----------
    query  : The question / problem statement.
    assets : Optional list of context URLs (unused at Level 1).

    Returns
    -------
    The answer string — NOT wrapped in JSON (gateway handles that).
    """
    client = _get_client()

    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    return _clean(raw)
