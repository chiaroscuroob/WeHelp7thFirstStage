import json
import urllib.request

def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8")

def try_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None
