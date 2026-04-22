"""
Challenge 01 — Agent
Level 1: Basic formatting / arithmetic queries.

Strategy for max cosine similarity:
  - Single deterministic LLM call with a densely few-shot prompt that locks
    in the exact sentence structure the eval engine expects.
  - Post-process to guarantee correct terminal punctuation (period).
  - temperature=0.0 for zero variance.
  - Distillation is NOT used — it over-compresses and kills cosine similarity.
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


# Dense few-shot prompt.  The examples show the exact output vocabulary
# and format the eval engine compares against.  More examples = stronger
# in-context learning signal for unseen hidden test cases.
SYSTEM_PROMPT = """\
You are an answer engine. Output ONLY the answer — one sentence, no preamble, \
no filler, no markdown.

FORMAT RULES:
- Arithmetic  → "The <word> is <value>."
    +  addition   → sum       e.g. "The sum is 25."
    -  subtract   → difference e.g. "The difference is 63."
    *  multiply   → product   e.g. "The product is 42."
    /  divide     → quotient  e.g. "The quotient is 12."
    %  modulo     → remainder e.g. "The remainder is 2."
    ** power      → result    e.g. "The result is 256."
- Yes/No       → "Yes." or "No." only (no extra words).
- Factual      → one short sentence, exactly as a textbook answer key.
- Never say "I", "Sure", "Of course", "Certainly", "Here is", "The answer is".
- Never repeat the question.
- Capitalise only the first word. End with a period.

EXAMPLES:
Q: What is 10 + 15?
A: The sum is 25.

Q: What is 100 - 37?
A: The difference is 63.

Q: What is 6 * 7?
A: The product is 42.

Q: What is 144 / 12?
A: The quotient is 12.

Q: What is 17 % 5?
A: The remainder is 2.

Q: What is 2 ** 8?
A: The result is 256.

Q: What is 2 to the power of 10?
A: The result is 1024.

Q: Is 17 a prime number?
A: Yes.

Q: Is 4 an odd number?
A: No.

Q: Is the sky blue?
A: Yes.

Q: What is the capital of France?
A: Paris.

Q: Who wrote Hamlet?
A: William Shakespeare.

Q: What is the boiling point of water in Celsius?
A: 100 degrees Celsius.

Q: What does HTTP stand for?
A: HyperText Transfer Protocol.

Q: What is the largest planet in the solar system?
A: Jupiter.

Q: What colour is a banana?
A: Yellow.

Q: Name three primary colors.
A: Red, blue, and yellow.

Q: What is the speed of light?
A: 299,792,458 metres per second.

Q: How many sides does a hexagon have?
A: Six.

Q: What is the chemical symbol for gold?
A: Au.

Q: What is the square root of 144?
A: 12.

Q: What is 50% of 200?
A: The result is 100.

Q: Convert 0 degrees Celsius to Fahrenheit.
A: 32 degrees Fahrenheit.

Q: What year did World War II end?
A: 1945.

Q: What is the plural of "mouse"?
A: Mice.
"""


def _clean(text: str) -> str:
    """
    Light post-processing:
    - Strip leading/trailing whitespace and quotes
    - Ensure answer ends with a period (if it doesn't end with punctuation)
    - Collapse multiple spaces
    """
    text = text.strip().strip('"').strip("'").strip()
    text = re.sub(r"\s+", " ", text)
    # Remove any "A:" prefix the model might accidentally include
    text = re.sub(r"^A:\s*", "", text, flags=re.IGNORECASE)
    # Ensure terminal punctuation
    if text and text[-1] not in ".!?":
        text += "."
    return text


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
            {"role": "user",   "content": f"Q: {query}\nA:"},
        ],
        temperature=0.0,
        max_tokens=80,   # answers at this level are ≤ ~15 words
        stop=["\n", "Q:"],  # stop before the model generates a new Q/A pair
    )

    raw = response.choices[0].message.content
    return _clean(raw)
