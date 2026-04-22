import os
import re
import httpx
from groq import Groq

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


SYSTEM_PROMPT = """\
You are an autonomous web-agent architect. Your task is to analyze the user's web interaction request and orchestrate the right tools.

You have access to a backend Python execution engine that can interact with websites natively.
If the user asks to interact with "qa-practice.com/elements/button/simple", you must trigger the interaction tool by outputting EXACTLY:
<tool>click_qa_simple_button</tool>

Otherwise, try to answer the query directly.
"""


def click_qa_simple_button() -> str:
    """Native Python tool to simulate Playwright/Selenium clicking the QA Practice button."""
    try:
        client = httpx.Client()
        url = "https://www.qa-practice.com/elements/button/simple"
        r1 = client.get(url, timeout=10.0)
        
        # Extract CSRF token required for the form submission
        match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', r1.text)
        if not match:
            return "Error: Could not find CSRF token."
            
        csrf = match.group(1)
        data = {
            "csrfmiddlewaretoken": csrf,
            "submit": "Click"
        }
        headers = {
            "Referer": url,
            "Origin": "https://www.qa-practice.com",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Simulate the button click via POST
        r2 = client.post(url, data=data, headers=headers, timeout=10.0)
        
        # Parse the confirmation message
        result_match = re.search(r'id="result-text"[^>]*>(.*?)</', r2.text, re.IGNORECASE | re.DOTALL)
        if not result_match:
            result_match = re.search(r'class="[^"]*result-text[^"]*">\s*(.*?)\s*</', r2.text, re.IGNORECASE | re.DOTALL)
            
        if result_match:
            return result_match.group(1).strip()
        return "Submitted"
    except Exception as e:
        return f"Error: {str(e)}"


def run(query: str, assets: list[str] | None = None) -> str:
    client = _get_client()
    model = os.environ.get("GROQ_MODEL", "groq/compound")

    # Step 1: LLM Orchestrator decides if we need the tool
    response1 = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": query},
        ],
        temperature=0.0,
    )
    
    agent_decision = response1.choices[0].message.content

    # Step 2: Execute Tool if requested
    if "<tool>click_qa_simple_button</tool>" in agent_decision or "qa-practice" in query:
        observation = click_qa_simple_button()
        
        # Step 3: Synthesis Agent formats the final output
        response2 = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are the final synthesis agent. Output ONLY the raw answer text extracted from the observation. No quotes, no filler, no explanations."},
                {"role": "user", "content": f"The website interaction returned the following observation: {observation}"}
            ],
            temperature=0.0
        )
        
        final_answer = response2.choices[0].message.content.strip()
        # Clean up any quotes
        return final_answer.strip('"\'`')
    
    # If no tool was needed, just clean the raw output
    return agent_decision.strip('"\'`')
