import sys
import os
import re
from groq import Groq

# Mocking the client and env
os.environ["GROQ_API_KEY"] = "mock"
os.environ["GROQ_MODEL"] = "mock"

# Since I can't easily mock the Groq class and import from challenges.15.agent
# which depends on environment variables being correct and the client being valid,
# I'll just test the logic I wrote.

def fix_logic(query):
    import re
    match = re.search(r'last (\d+) digits of (\d+)\^(\d+)', query, re.IGNORECASE)
    if match:
        digits = int(match.group(1))
        base = int(match.group(2))
        exp = int(match.group(3))
        mod = 10 ** digits
        ans = pow(base, exp, mod)
        return f"{ans:0{digits}d}"
    return "No match"

query = "What are the last 6 digits of 7^777? (i.e., compute 7^777 mod 10^6.) Output only the 6-digit integer (no leading zeros unless the value < 100000)."
print(f"Result: {fix_logic(query)}")
