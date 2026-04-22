import httpx
import re

url = "https://en.wikipedia.org/wiki/1936_Summer_Olympics"
r = httpx.get(url, timeout=10.0)
html = r.text

# We need the emblem inside table class="infobox vevent". Then td class="infobox-image".
# Let's find the infobox.
infobox_match = re.search(r'<table[^>]*class="infobox[^>]*>(.*?)</table>', html, re.IGNORECASE | re.DOTALL)
if infobox_match:
    infobox_html = infobox_match.group(1)
    # Find td class="infobox-image"
    td_match = re.search(r'<td[^>]*class="[^"]*infobox-image[^"]*"[^>]*>(.*?)</td>', infobox_html, re.IGNORECASE | re.DOTALL)
    if td_match:
        td_html = td_match.group(1)
        # Find img src
        img_match = re.search(r'<img[^>]+src="([^"]+)"', td_html, re.IGNORECASE)
        if img_match:
            print("SRC:", img_match.group(1))
        else:
            print("NO IMG FOUND")
    else:
        # Wikipedia sometimes just has <tr><td colspan="2" class="infobox-image">
        img_match = re.search(r'<td[^>]*infobox-image[^>]*>.*?<img[^>]+src="([^"]+)"', infobox_html, re.IGNORECASE | re.DOTALL)
        if img_match:
            print("SRC:", img_match.group(1))
        else:
            print("NO TD FOUND")
else:
    print("NO INFOBOX FOUND")
