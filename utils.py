import re
import sys

def normalize_phone(s: str) -> str:
    s = (s or "").replace("(", "").replace(")", "").replace(" ", "")
    s = s.replace("+886", "0")
    return re.sub(r"[^\d-]", "", s)

def extract_district(addr_ch: str) -> str:
    """從中文地址擷取行政區，回傳像『中正區』『信義區』這樣的字串。"""
    if not addr_ch:
        return ""
    addr = addr_ch.replace("臺", "台")  # 規一「台/臺」
    # 找出所有片段（最後一個通常是行政區）
    matches = re.findall(r"([\u4e00-\u9fff]{1,3}[區鎮鄉])", addr)
    if not matches:
        return ""
    dist = matches[-1]
    # 偶爾會抓到『市中山區』這種，把開頭的『市』去掉
    if dist.startswith("市"):
        dist = dist[1:]
    return dist

def warn(msg: str):
    print(f"[WARN] {msg}", file=sys.stderr)
