"""
Challenge 05 — Agent
Comparison queries: who scored highest, what is bigger, etc.
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
You answer comparison questions.

RULES:
- Output ONLY the answer. No explanation. No filler words. No preamble.
- If the question asks who/what is highest/greatest/largest/most/biggest, return only the name of that thing.
- If the question asks who/what is lowest/least/smallest/worst, return only the name of that thing.
- If two things are exactly equal, respond with the names of those two things separated by a space and first letter capitalized.
- If items are not numbers (e.g. names, words, objects), compare them by length/size as appropriate and return what is asked.
- Match the exact format of the expected answer. Single word or name only.

Example:
Q: Alice scored 80, Bob scored 90. Who scored highest?
A: Bob
"""


def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^A:\s*", "", text, flags=re.IGNORECASE)
    # Remove any trailing period or punctuation the model might add
    text = text.rstrip(".")
    return text.strip()


def run(query: str, assets: list[str] | None = None) -> str:
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
