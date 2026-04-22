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
You are an expert formatting engine. Your task is to answer the query strictly adhering to ALL formatting constraints provided.

RULES:
- Follow all formatting instructions meticulously (e.g., UPPERCASE, specific delimiters like pipe '|', NO spaces).
- If the prompt asks for a list with NO spaces around delimiters, ensure there are absolutely no spaces (e.g., "ITEM1|ITEM2").
- Output ONLY the final requested text. No explanation, no filler words, no preamble, and no markdown formatting.
- Do NOT wrap the output in quotes unless explicitly requested by the query.
- Ensure the logical order of items is correct as requested (e.g., first to last).
"""


def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(A|Answer|Result|Output):\s*", "", text, flags=re.IGNORECASE)
    # Strip any accidental surrounding quotes or backticks
    text = text.strip('"\'`')
    return text.strip()


def run(query: str, assets: list[str] | None = None) -> str:
    client = _get_client()

    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    return _clean(raw)
