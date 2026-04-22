# SKILL: QA Practice — Simple Button Interaction

## Purpose
Navigate to the QA Practice "Simple Button" page, click the **Click** button, capture the confirmation message that appears, and return it as the answer.

---

## Target URL
```
https://www.qa-practice.com/elements/button/simple
```

---

## Page Structure (Reference)

| Element | Type | Selector / Locator |
|---|---|---|
| "Simple button" tab | `<a>` link | `a[href="/elements/button/simple"]` or link text `Simple button` |
| Main **Click** button | `<button>` or `<input type="button">` | `#submit-bt`, `button:has-text("Click")`, or `input[value="Click"]` |
| Confirmation message box | `<div>` / `<p>` that appears after click | `#result`, `.result`, `p.result-text`, or any element that becomes visible after the button click |

> **Note:** Selectors were derived from page analysis. If a selector fails, fall back to the alternatives listed or use text-based locators.

---

## Step-by-Step Instructions

### Step 1 — Navigate to the page
```
Open / navigate to: https://www.qa-practice.com/elements/button/simple
```
- Wait for the page to fully load (wait for `DOMContentLoaded` or `networkidle`).
- Confirm you are on the correct page by verifying the page title contains **"Simple Button"** or the URL matches exactly.

### Step 2 — Activate the "Simple button" tab
- The URL `https://www.qa-practice.com/elements/button/simple` already opens the **Simple button** tab directly.
- If you are already on this URL, the tab is active — **no extra click is needed**.
- If redirected to a parent page (`/elements/button`), locate and click the link with text `Simple button`:
  ```
  Click: a[href="/elements/button/simple"]   // CSS selector
  Click: link text "Simple button"           // text-based fallback
  ```
- Wait for navigation to settle before proceeding.

### Step 3 — Click the "Click" button
Locate the button using the following selectors **in priority order** (try each until one succeeds):

| Priority | Selector | Notes |
|---|---|---|
| 1 | `#submit-bt` | ID-based — most reliable |
| 2 | `button:has-text("Click")` | Playwright text selector |
| 3 | `input[value="Click"]` | In case it is an `<input>` element |
| 4 | `xpath=//button[normalize-space()='Click']` | XPath fallback |
| 5 | `xpath=//input[@value='Click']` | XPath fallback for input |

**Action:** Click the resolved element.

```python
# Playwright (Python) example
page.locator("#submit-bt").click()

# Selenium (Python) example
driver.find_element(By.ID, "submit-bt").click()
```

### Step 4 — Wait for the confirmation message
After clicking, a confirmation message will appear in a result box on the same page. Wait for it to become visible:

```python
# Playwright — wait for result element to be visible
page.wait_for_selector("#result", state="visible", timeout=5000)

# Selenium — explicit wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.ID, "result"))
)
```

**Fallback selectors for the confirmation box (try in order):**
1. `#result`
2. `.result`
3. `p.result-text`
4. `xpath=//p[contains(@class,'result')]`
5. Any element that was **not present before** the click and **becomes visible after** — use DOM diffing if needed.

### Step 5 — Extract and return the answer
Read the **text content** of the confirmation element:

```python
# Playwright
answer = page.locator("#result").inner_text()

# Selenium
answer = driver.find_element(By.ID, "result").text
```

- Strip leading/trailing whitespace: `answer = answer.strip()`
- **Return `answer` as the final result.**

---

## Complete Pseudocode Workflow

```
FUNCTION solve_simple_button_task():
    1. navigate_to("https://www.qa-practice.com/elements/button/simple")
    2. wait_for_page_load()
    3. assert current_url == "https://www.qa-practice.com/elements/button/simple"
       OR click link("Simple button") if not already there
    4. button = find_element(priority_selectors=["#submit-bt",
                                                  "button:has-text('Click')",
                                                  "input[value='Click']"])
    5. button.click()
    6. confirmation = wait_and_get_text(selectors=["#result", ".result",
                                                    "p.result-text"],
                                         timeout=5s)
    7. RETURN confirmation.strip()
```

---

## Error Handling

| Scenario | Action |
|---|---|
| Page does not load | Retry navigation up to 3 times; raise error if all fail |
| "Click" button not found | Try all fallback selectors; log which selector was attempted |
| Confirmation box never appears | Wait up to 10 s total; if still missing, take a screenshot and raise descriptive error |
| Confirmation text is empty | Re-read after 1 s delay; if still empty, return raw `innerHTML` |
| CAPTCHA or access block | Report to the caller — do not attempt to bypass |

---

## Expected Output

The task answer is the **text content** of the confirmation box that appears after clicking the button.

Based on the page requirements ("After pressing the button, the user should be shown confirmation that the button was pressed"), the message is expected to be something like:

```
"Well done!"
```
or a similar short confirmation string. **Do not hard-code this value** — always read it dynamically from the page.

---

## Dependencies / Environment

| Tool | Minimum Version | Notes |
|---|---|---|
| Playwright | 1.30+ | Preferred; supports `has-text` and `wait_for_selector` |
| Selenium | 4.0+ | Fallback; use `WebDriverWait` for dynamic elements |
| Python | 3.8+ | Or Node.js 18+ for Playwright JS |
| Browser | Chromium / Chrome | Headless mode supported |

---

## Quick-Reference Cheat Sheet

```
URL       : https://www.qa-practice.com/elements/button/simple
Tab click : a[href="/elements/button/simple"]   (skip if already on URL)
Button    : #submit-bt  →  button:has-text("Click")  →  input[value="Click"]
Result    : #result  →  .result  →  p.result-text
Output    : result_element.inner_text().strip()
```
