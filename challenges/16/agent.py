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
2. Inside the <think> block, carefully compute every single element C[i][j].
3. After closing the </think> tag, output ONLY the final result matrix in the EXACT expected format.
4. The exact formatting expects NO commas. Rows are separated by a single space.
5. Each row is wrapped in brackets, and there is a leading space before the first number in a row if it's 2 digits to align with 3-digit numbers.
6. EXACT EXAMPLE FORMAT: [[ 30 24 18] [ 84 69 54] [138 114 90]]
7. The final answer must contain NO filler words, NO markdown, and NO explanations.
"""


def _clean(text: str) -> str:
    # Remove the <think>...</think> block
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    
    # Standard cleanup
    text = re.sub(r"^(A|Answer|Result|Output):\s*", "", text, flags=re.IGNORECASE)
    text = text.strip('"\'`')
    text = text.rstrip(".")
    
    # Remove commas but PRESERVE internal spacing
    text = text.replace(',', '')
    # Replace multiple newlines/tabs with a single space to keep it on one line
    text = re.sub(r'[\r\n\t]+', ' ', text)
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
