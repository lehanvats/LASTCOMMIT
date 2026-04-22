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
You are an expert data extractor. Find the exact item in the log that matches the user's criteria.

RULES FOR YOUR OUTPUT:
- Read the log from start to finish and find the FIRST item that matches ALL conditions.
- Format the output EXACTLY as the expected output. 
- If extracting a transaction (e.g. "Steve paid $210"), you MUST format the output EXACTLY as "[Name] paid the amount of $[Amount]."
- Output ONLY the final answer. No explanation, no filler words, no preamble.
- No leading or trailing quotation marks.
"""


def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(A|Answer|Result|Output):\s*", "", text, flags=re.IGNORECASE)
    # Strip any accidental surrounding quotes
    text = text.strip('"\'')
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
