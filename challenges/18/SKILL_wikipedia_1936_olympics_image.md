# SKILL: Wikipedia 1936 Summer Olympics — Infobox Image Extraction

## Purpose
Navigate to the 1936 Summer Olympics Wikipedia page, locate the infobox table at the top of the article, find the Olympics emblem image inside it, extract the `src` attribute of that `<img>` element, and return the full image URL as the answer.

---

## Target URL
```
https://en.wikipedia.org/wiki/1936_Summer_Olympics
```

---

## Page DOM Structure (Reference)

Wikipedia articles for Olympics events follow a consistent infobox pattern:

```html
<!-- Infobox container — always a <table> near the top of the article body -->
<table class="infobox vevent">
  <tbody>
    <tr>
      <td colspan="2" class="infobox-image">
        <!-- The emblem/logo image lives here -->
        <img src="//upload.wikimedia.org/wikipedia/commons/thumb/.../Xpx-....png"
             srcset="..."
             width="..."
             height="..."
             alt="..." />
      </td>
    </tr>
    <!-- ... more rows with key-value facts ... -->
  </tbody>
</table>
```

### Key DOM facts
| Property | Value |
|---|---|
| Infobox tag | `<table>` |
| Infobox classes | `infobox vevent` (both classes present) |
| Image parent cell | `<td class="infobox-image">` |
| Image tag | `<img>` — first `<img>` inside the infobox |
| `src` format | Protocol-relative: `//upload.wikimedia.org/wikipedia/commons/thumb/...` |
| Full URL prefix | Prepend `https:` to get `https://upload.wikimedia.org/...` |

---

## Step-by-Step Instructions

### Step 1 — Navigate to the page
```
Open / navigate to: https://en.wikipedia.org/wiki/1936_Summer_Olympics
```
- Wait for the DOM to fully load (`DOMContentLoaded` or `networkidle`).
- Confirm the page `<h1>` or `<title>` contains **"1936 Summer Olympics"**.

### Step 2 — Locate the infobox
Find the infobox table using the following selectors **in priority order**:

| Priority | Selector | Notes |
|---|---|---|
| 1 | `table.infobox.vevent` | Most specific — both classes required |
| 2 | `table.infobox` | Broader match; picks first infobox on page |
| 3 | `xpath=//table[contains(@class,'infobox')]` | XPath fallback |
| 4 | `xpath=//table[contains(@class,'vevent')]` | XPath fallback |

```python
# Playwright (Python)
infobox = page.locator("table.infobox.vevent")

# Selenium (Python)
infobox = driver.find_element(By.CSS_SELECTOR, "table.infobox.vevent")
```

> **Validation:** Assert the infobox element exists and is visible before proceeding.

### Step 3 — Find the image element inside the infobox
Scope the image search **within** the already-found infobox element to avoid picking up unrelated page images:

```python
# Playwright — scoped to infobox
img_element = page.locator("table.infobox.vevent img").first

# Selenium — scoped to infobox element
img_element = infobox.find_element(By.TAG_NAME, "img")
```

**Fallback selectors (try in order if the above fails):**
1. `table.infobox.vevent td.infobox-image img`
2. `table.infobox.vevent tbody tr:first-child img`
3. `table.infobox img:first-of-type`
4. `xpath=//table[contains(@class,'infobox')]//td[contains(@class,'infobox-image')]//img`

### Step 4 — Extract the `src` attribute
Read the `src` attribute from the located `<img>` element:

```python
# Playwright
src = img_element.get_attribute("src")

# Selenium
src = img_element.get_attribute("src")
```

### Step 5 — Normalize the URL
Wikipedia image `src` values are **protocol-relative** (begin with `//`). Convert to a full HTTPS URL:

```python
if src.startswith("//"):
    src = "https:" + src

# Final answer
return src
```

**Expected output format:**
```
https://upload.wikimedia.org/wikipedia/commons/thumb/<hash>/<filename>/<width>px-<filename>
```

Example pattern (exact values vary by Wikipedia's CDN):
```
https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/1936_Summer_Olympics_logo.svg/150px-1936_Summer_Olympics_logo.svg.png
```

---

## Complete Pseudocode Workflow

```
FUNCTION extract_infobox_image_src():
    1.  navigate_to("https://en.wikipedia.org/wiki/1936_Summer_Olympics")
    2.  wait_for_page_load()
    3.  assert page_title contains "1936 Summer Olympics"

    4.  infobox = find_element(selectors=[
            "table.infobox.vevent",
            "table.infobox",
            "xpath=//table[contains(@class,'infobox')]"
        ])
    5.  assert infobox exists

    6.  img = find_element_within(infobox, selectors=[
            "img",
            "td.infobox-image img",
            "tbody tr:first-child img"
        ])
    7.  assert img exists

    8.  src = img.get_attribute("src")
    9.  assert src is not None and src != ""

    10. IF src starts with "//"
            src = "https:" + src

    11. RETURN src
```

---

## Code Examples

### Playwright (Python) — Full Implementation
```python
from playwright.sync_api import sync_playwright

def extract_infobox_image_src():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://en.wikipedia.org/wiki/1936_Summer_Olympics")
        page.wait_for_load_state("domcontentloaded")

        # Locate infobox image (scoped)
        img_locator = page.locator("table.infobox.vevent img").first

        # Extract src
        src = img_locator.get_attribute("src")
        if not src:
            raise ValueError("Image src attribute not found.")

        # Normalize protocol-relative URL
        if src.startswith("//"):
            src = "https:" + src

        browser.close()
        return src

answer = extract_infobox_image_src()
print(answer)
```

### Selenium (Python) — Full Implementation
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_infobox_image_src():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get("https://en.wikipedia.org/wiki/1936_Summer_Olympics")

    # Wait for infobox to be present
    infobox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.infobox.vevent"))
    )

    # Find first image inside infobox
    img = infobox.find_element(By.TAG_NAME, "img")

    # Extract and normalize src
    src = img.get_attribute("src")
    if not src:
        raise ValueError("Image src attribute not found.")
    if src.startswith("//"):
        src = "https:" + src

    driver.quit()
    return src

answer = extract_infobox_image_src()
print(answer)
```

### DOM / JavaScript (Browser Console) — Quick Verification
```javascript
// Run in browser DevTools console to verify the selector and src
const infobox = document.querySelector("table.infobox.vevent");
const img     = infobox ? infobox.querySelector("img") : null;
const src     = img ? img.getAttribute("src") : null;
const fullSrc = src && src.startsWith("//") ? "https:" + src : src;
console.log("Image src:", fullSrc);
```

---

## Error Handling

| Scenario | Action |
|---|---|
| Page fails to load | Retry up to 3 times; raise descriptive error if all fail |
| `table.infobox.vevent` not found | Try `table.infobox`; if still missing, check if Wikipedia changed its markup |
| No `<img>` inside infobox | Try broader selectors listed above; log all `<img>` tags found on page for debugging |
| `src` attribute is `None` or empty | Try `data-src` (lazy-load fallback); or `srcset` (parse first URL from value) |
| `src` is a relative path (`/wiki/...`) | Prepend `https://en.wikipedia.org` to form a full URL |
| `src` is already absolute (`https://...`) | Return as-is, no transformation needed |

---

## Selector Quick-Reference

```
URL      : https://en.wikipedia.org/wiki/1936_Summer_Olympics
Infobox  : table.infobox.vevent
           → fallback: table.infobox
Image    : table.infobox.vevent img  (first match)
           → fallback: table.infobox.vevent td.infobox-image img
src attr : img.get_attribute("src")
Normalize: prepend "https:" if src starts with "//"
Output   : full HTTPS URL string
```

---

## Dependencies / Environment

| Tool | Minimum Version | Notes |
|---|---|---|
| Playwright | 1.30+ | Preferred for `.first` chaining and `get_attribute` |
| Selenium | 4.0+ | Use `WebDriverWait` for robust element detection |
| Python | 3.8+ | Or Node.js 18+ for Playwright JS |
| Browser | Chromium / Chrome / Firefox | Headless mode fully supported |
| Network | Public internet access required | Wikipedia is publicly accessible |
