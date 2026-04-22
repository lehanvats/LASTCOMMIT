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
- Identify the FIRST full item, event, or transaction that matches ALL specified conditions.
- Do NOT just output a name. Output the COMPLETE matching action or phrase.
- Format the output exactly as requested or expected.
- For example, if extracting a transaction like "Steve paid $210", you must output the full phrase formatted as: "Steve paid the amount of $210."
- Maintain this level of completeness for any extracted item (e.g. including the action and the value).
- Output ONLY the final answer. No filler words, preamble, or explanation.
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
        model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    return _clean(raw)
