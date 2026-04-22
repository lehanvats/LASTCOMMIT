import httpx
import re

def run():
    client = httpx.Client()
    url = "https://www.qa-practice.com/elements/button/simple"
    r1 = client.get(url)
    
    match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', r1.text)
    if match:
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
        r2 = client.post(url, data=data, headers=headers)
        
        # Find result: <p class="result-text">Submitted</p> or <p id="result-text" ...>
        result_match = re.search(r'id="result-text"[^>]*>(.*?)</', r2.text, re.IGNORECASE | re.DOTALL)
        if not result_match:
            result_match = re.search(r'class="[^"]*result-text[^"]*">\s*(.*?)\s*</', r2.text, re.IGNORECASE | re.DOTALL)
        print(result_match.group(1).strip() if result_match else "NOT FOUND")
    else:
        print("NO CSRF FOUND")

run()
