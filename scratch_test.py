import importlib
import os

with open('.env') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            # Remove inline comments
            val = val.split('#')[0].strip()
            os.environ[key.strip()] = val

agent = importlib.import_module("challenges.05.agent")

test_cases = [
    "Alice scored 80, Bob scored 90. Who scored highest?",
    "Apple is 5 bytes, Banana is 6 bytes. What is larger?",
    "X has 10, Y has 10. Who has most?"
]

for q in test_cases:
    ans = agent.run(q)
    print(f"Q: {q}\nA: {ans}\n")
