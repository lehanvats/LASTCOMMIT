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
You are a logical inference engine. Your task is to analyze the provided input and identify the specific entity or action that satisfies all given logical constraints.

RULES:
- Identify the FIRST item, user, or transaction that matches ALL specified conditions.
- Output ONLY the final answer in the exact format requested.
- If the answer involves a user payment, format it exactly as: "[Name] paid the amount of $[Amount]."
- No filler words, preamble, or explanation.
- No quotation marks in the output.
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
