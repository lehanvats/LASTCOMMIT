import re

def fix_payload(s: str) -> str:
    match_start = re.search(r'"query"\s*:\s*"', s)
    if not match_start:
        return s
    start_idx = match_start.end()
    
    if '"assets"' in s[start_idx:]:
        match_end = re.search(r'"\s*,\s*"assets"', s[start_idx:])
        if match_end:
            end_idx = start_idx + match_end.start()
            query_val = s[start_idx:end_idx]
            query_val = query_val.replace('\\"', '"').replace('"', '\\"')
            return s[:start_idx] + query_val + s[end_idx:]
            
    match_end = re.search(r'"\s*}', s[start_idx:])
    if match_end:
        last_brace = s.rfind('}')
        if last_brace != -1:
            last_quote = s.rfind('"', start_idx, last_brace)
            # Make sure there are only spaces between last_quote and last_brace
            if s[last_quote+1:last_brace].strip() == '':
                query_val = s[start_idx:last_quote]
                query_val = query_val.replace('\\"', '"').replace('"', '\\"')
                return s[:start_idx] + query_val + s[last_quote:]
                
    return s

s1 = '{\n  "query": "Apply rules in order to input number 6: Rule 1: If even → double it. If odd → add 10. Rule 2: If result > 20 → subtract 5. Otherwise → add 3. Rule 3: If final result divisible by 3 → output "FIZZ". Otherwise → output the number.",\n  "assets": ["https://asset-url-1.com", "https://asset-url-2.com"]\n}'
s2 = '{"assets": [], "query": "hello "world"!"}'

print(fix_payload(s1))
print(fix_payload(s2))
