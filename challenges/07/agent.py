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
You are an expert logical rule engine. You will be given an initial number and a set of rules to apply sequentially.
Follow the rules step-by-step mentally to calculate the final result.

RULES FOR YOUR OUTPUT:
- Output ONLY the final result. No explanation, no filler words, no preamble.
- Do NOT output your step-by-step thoughts.
- If the final result is a word (like FIZZ), output exactly that word WITHOUT surrounding quotes.
- If the final result is a number, output just the number.
- Ensure the answer exactly matches the expected format.
- No leading or trailing punctuations or quotation marks.
"""


def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(A|Answer|Result|Output):\s*", "", text, flags=re.IGNORECASE)
    text = text.rstrip(".")
    # Strip any accidental surrounding quotes
    text = text.strip('"\'')
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
