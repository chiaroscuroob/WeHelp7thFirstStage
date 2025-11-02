import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}
COOKIES = {
    "over18": "1",  # 穩妥起見，帶著通關 cookie
}

def fetch_list_page(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=10)
    resp.encoding = "utf-8"
    return resp.text

def find_prev_page(html: str):
    soup = BeautifulSoup(html, "html.parser")
    btns = soup.select(".btn.wide")
    for a in btns:
        if "上頁" in a.text:
            return a.get("href")
    return None

def _parse_nrec(nrec_text: str) -> int:
    t = (nrec_text or "").strip()
    if t == "爆":
        return 100
    if t.startswith("X") and t[1:].isdigit():
        return -int(t[1:])
    if t.isdigit():
        return int(t)
    return 0

def parse_list_items(html: str):
    """回傳清單條目（排除刪文）：[{title, href, nrec}]"""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select(".r-ent")
    items = []
    for r in rows:
        a = r.select_one(".title a")
        if not a:
            continue  # 刪文或無連結
        title = a.text.strip()
        href = a.get("href")
        nrec_text = r.select_one(".nrec").text if r.select_one(".nrec") else ""
        items.append({"title": title, "href": href, "nrec": _parse_nrec(nrec_text)})
    return items

def fetch_article_time(url: str) -> str:
    """抓文章頁時間字串；若無則回空字串。"""
    try:
        resp = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        metas = soup.select(".article-meta-value")
        if len(metas) >= 4:
            # 例：Sat Oct 25 14:57:33 2025 或 Sun Nov␠␠2 12:36:42 2025
            t = metas[3].get_text(strip=True)
            if re.match(r"^[A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}$", t):
                return t
        return ""
    except requests.RequestException:
        return ""
