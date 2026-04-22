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

BACKGROUND KNOWLEDGE:
A Latin square of order n is an n x n array filled with n different symbols, each occurring exactly once in each row and exactly once in each column.

RULES:
1. You MUST write your step-by-step reasoning inside <think>...</think> XML tags.
2. Carefully analyze all constraints, definitions, permutations, and mathematical properties related to Latin squares or combinatorics.
3. After closing the </think> tag, output ONLY the final requested answer.
4. The final answer must contain NO filler words, NO punctuation, NO formatting (no markdown), and NO explanations.
5. If the question asks for an integer, output ONLY the integer.

Example format:
<think>
1. Identify the formula or combinatorics for Latin squares of order 4...
2. Calculate the number of reduced Latin squares...
3. Multiply by n!(n-1)! to find the total distinct Latin squares...
4. The result is...
</think>
576
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
