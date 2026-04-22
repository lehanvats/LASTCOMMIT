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
You are an expert mathematician and logic solver. You must solve the problem step-by-step to ensure absolute correctness.

RULES:
1. You MUST write your step-by-step reasoning inside <think>...</think> XML tags.
2. Carefully analyze all constraints, modular arithmetic properties, Euler's totient function, or exponentiation techniques.
3. After closing the </think> tag, output ONLY the final requested answer.
4. The final answer must contain NO filler words, NO punctuation, NO formatting (no markdown), and NO explanations.
5. If the question asks for an integer, output ONLY the integer (e.g. without leading zeros unless specified).

Example format:
<think>
1. Identify the base and exponent...
2. Apply Euler's theorem or repeated squaring to find the result modulo 10^6...
3. Calculate the final 6 digits...
</think>
610543
"""


def _clean(text: str) -> str:
    # Remove the <think>...</think> block including its content
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    
    # Standard cleanup for the remaining final answer
    text = re.sub(r"^(A|Answer|Result|Output):\s*", "", text, flags=re.IGNORECASE)
    text = text.strip('"\'`')
    text = text.rstrip(".")
    return text.strip()


def run(query: str, assets: list[str] | None = None) -> str:
    client = _get_client()

    response = client.chat.completions.create(
        model=os.environ.get("GROQ_MODEL", "groq/compound"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ],
        temperature=0.0,
    )

    raw = response.choices[0].message.content
    return _clean(raw)
