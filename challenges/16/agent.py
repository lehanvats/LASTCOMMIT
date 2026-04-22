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
You are an expert mathematician and logic solver. You must compute the matrix multiplication carefully and flawlessly.

HOW TO COMPUTE MATRIX MULTIPLICATION (A x B):
To find the element at row i and column j of the result matrix C, multiply each element of row i of matrix A by the corresponding element of column j of matrix B, and sum the results.
Formula: C[i][j] = A[i][1]*B[1][j] + A[i][2]*B[2][j] + ... + A[i][n]*B[n][j]

RULES:
1. You MUST write your step-by-step reasoning inside <think>...</think> XML tags.
2. Inside the <think> block, carefully compute every single element C[i][j] by showing the explicit multiplication and sum.
3. After closing the </think> tag, output ONLY the final result matrix in the EXACT expected format.
4. The exact formatting expects NO commas between numbers and NO commas between rows. (e.g. [[ 30 24 18] [ 84 69 54] [138 114 90]])
5. Ensure numbers align gracefully with single spaces, but do not add newlines. Keep the entire result on ONE single line.
6. The final answer must contain NO filler words, NO formatting (no markdown blocks like ```), and NO explanations.
"""


def _clean(text: str) -> str:
    # Remove the <think>...</think> block including its content
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    
    # Standard cleanup for the remaining final answer
    text = re.sub(r"^(A|Answer|Result|Output):\s*", "", text, flags=re.IGNORECASE)
    text = text.strip('"\'`')
    text = text.rstrip(".")
    # Squeeze multiple spaces into a single space, just in case
    text = re.sub(r'\s+', ' ', text)
    # Ensure it exactly matches the format [[ a b ] [ c d ]] without commas
    text = text.replace(',', '')
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
