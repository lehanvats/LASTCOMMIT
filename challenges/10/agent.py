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
You are an expert fact-checking and logic engine. Your task is to answer questions strictly based on the provided explicit rules and claims.

RULES:
- Read carefully to see if the user provides a "Rule:" about which claims to trust (e.g. "[VERIFIED]").
- ALWAYS prioritize the claim that satisfies the trust rule explicitly given in the prompt, even if your internal knowledge says otherwise, but especially when dealing with conflicting claims.
- Output ONLY the final requested information (e.g., if asked for "city name only", output just the city).
- Do NOT output explanations, filler words, preamble, or formatting like quotes or periods unless requested.
"""


def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(A|Answer|Result|Output):\s*", "", text, flags=re.IGNORECASE)
    # Strip any accidental surrounding quotes or backticks
    text = text.strip('"\'`')
    text = text.rstrip(".")
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
