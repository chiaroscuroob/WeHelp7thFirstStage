# week3/task1/parsers.py
# -*- coding: utf-8 -*-
import re, io, csv
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

# ---------- 基本工具 ----------
def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def _norm_key(s: str) -> str:
    """標準化鍵名：小寫、移除空白/底線/點號。"""
    return re.sub(r"[ \t\._]", "", (s or "").lower())

def _pick(d: Dict, candidates: List[str]) -> str:
    """
    從 dict d 取符合候選鍵名的值：
    - 鍵名不分大小寫
    - 忽略空白、底線、點號
    - 支援相互包含（e.g. englishname / nameen / english_name）
    """
    if not isinstance(d, dict):
        return ""
    nd = {_norm_key(k): v for k, v in d.items()}
    norm_candidates = [_norm_key(k) for k in candidates]

    # 先做精確比對
    for nk in norm_candidates:
        if nk in nd and nd[nk] not in (None, ""):
            return str(nd[nk])

    # 再做模糊包含（兩邊其一包含另一個）
    for nk in norm_candidates:
        for key, val in nd.items():
            if val in (None, ""):
                continue
            if nk in key or key in nk:
                return str(val)
    return ""

def _to_int(s: Any) -> int:
    return int(re.sub(r"\D", "", str(s or "")) or 0)

# ---------- 找出 list[dict]（可遞迴） ----------
def _find_rows(obj: Any) -> Optional[List[Dict]]:
    """回傳第一個符合的 list[dict]；若找不到傳回 None。"""
    if isinstance(obj, list):
        if len(obj) == 0 or isinstance(obj[0], dict):
            return obj
        return None
    if isinstance(obj, dict):
        # 常見容器鍵名優先
        for key in ("data", "items", "result", "records", "hotels"):
            if key in obj:
                rows = _find_rows(obj[key])
                if rows is not None:
                    return rows
        # 其他鍵名遞迴
        for v in obj.values():
            rows = _find_rows(v)
            if rows is not None:
                return rows
    return None

# ---------- CSV 解析（中/英都可用） ----------
def _parse_hotels_csv(text: str, lang: str) -> Optional[List[Dict]]:
    if not isinstance(text, str) or not text.strip():
        return None
    lines = text.splitlines()
    if not lines:
        return None
    # 粗判：第一行要像 CSV 表頭
    if "," not in lines[0]:
        return None

    try:
        reader = csv.DictReader(io.StringIO(text))
    except Exception:
        return None

    # 鍵名候選（盡量涵蓋變體）
    if lang == "en":
        name_keys  = ["EnglishName", "Name_en", "name_en", "Name EN", "Name"]
        addr_keys  = ["EnglishAddress", "Address_en", "address_en", "English Addr", "Address"]
        phone_keys = ["Phone", "Tel", "phone", "Telephone", "聯絡電話", "電話"]
        room_keys  = ["RoomCount", "Rooms", "room", "rooms", "房間數", "總房間數"]
    else:
        name_keys  = ["ChineseName", "Name_ch", "name_ch", "旅館名稱", "名稱", "旅館名"]
        addr_keys  = ["ChineseAddress", "Address_ch", "address_ch", "地址", "住址"]
        phone_keys = ["Phone", "phone", "Tel", "電話", "聯絡電話"]
        room_keys  = ["RoomCount", "Rooms", "room", "rooms", "房間數", "總房間數"]

    rows: List[Dict] = []
    try:
        for r in reader:
            if lang == "en":
                rows.append({
                    "name_en": _clean(_pick(r, name_keys)),
                    "addr_en": _clean(_pick(r, addr_keys)),
                    "phone":   _clean(_pick(r, phone_keys)),
                    "rooms":   _to_int(_pick(r, room_keys)),
                })
            else:
                rows.append({
                    "name_ch": _clean(_pick(r, name_keys)),
                    "addr_ch": _clean(_pick(r, addr_keys)),
                    "phone":   _clean(_pick(r, phone_keys)),
                    "rooms":   _to_int(_pick(r, room_keys)),
                })
    except Exception:
        return None

    # 若完全抓不到名稱，視為非本題 CSV
    if not rows or all(not (rows[0].get("name_en") or rows[0].get("name_ch")) for _ in [0]):
        return None
    return rows

# ---------- HTML 備援 ----------
class _HotelsHTMLParser(HTMLParser):
    """非常保守的表格解析器：假設 <tr><td>依序為名稱/地址/(電話)/房數。"""
    def __init__(self, lang: str):
        super().__init__()
        self.lang = lang
        self.rows: List[Dict] = []
        self._cur: Dict[str, Any] = {}
        self._td_idx = -1
        self._in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._cur = {}
            self._td_idx = -1
        if tag == "td":
            self._in_td = True
            self._td_idx += 1

    def handle_endtag(self, tag):
        if tag == "tr" and self._cur:
            self.rows.append(self._cur)
            self._cur = {}
        if tag == "td":
            self._in_td = False

    def handle_data(self, data):
        if not self._in_td:
            return
        txt = data.strip()
        if not txt:
            return
        if self._td_idx == 0:
            self._cur["name_ch" if self.lang == "ch" else "name_en"] = txt
        elif self._td_idx == 1:
            self._cur["addr_ch" if self.lang == "ch" else "addr_en"] = txt
        elif self._td_idx == 2 and self.lang == "ch":
            self._cur["phone"] = txt
        elif self._td_idx == 3 and self.lang == "ch":
            self._cur["rooms"] = _to_int(txt)

def _parse_hotels_html(html: str, lang: str) -> List[Dict]:
    p = _HotelsHTMLParser(lang=lang)
    p.feed(html or "")
    rows: List[Dict] = []
    for r in p.rows:
        rows.append({
            "name_ch": r.get("name_ch", "") if lang == "ch" else "",
            "addr_ch": r.get("addr_ch", "") if lang == "ch" else "",
            "name_en": r.get("name_en", "") if lang == "en" else "",
            "addr_en": r.get("addr_en", "") if lang == "en" else "",
            "phone": r.get("phone", ""),
            "rooms": int(r.get("rooms") or 0),
        })
    return rows

# ---------- 對外主函式 ----------
def parse_hotels_ch(data: Any) -> List[Dict]:
    # 1) JSON：找 list[dict]
    rows = _find_rows(data)
    if rows is not None:
        out: List[Dict] = []
        for d in rows:
            out.append({
                "name_ch": _clean(_pick(d, ["name","ChineseName","旅館名稱","名稱","旅館名"])),
                "addr_ch": _clean(_pick(d, ["address","ChineseAddress","地址","住址"])),
                "phone":   _clean(_pick(d, ["phone","Phone","Tel","電話","聯絡電話"])),
                "rooms":   _to_int(_pick(d, ["room","RoomCount","Rooms","房間數","總房間數"])),
            })
        return out
    # 2) CSV
    csv_rows = _parse_hotels_csv(str(data), lang="ch")
    if csv_rows is not None:
        return csv_rows
    # 3) HTML
    return _parse_hotels_html(str(data), lang="ch")

def parse_hotels_en(data: Any) -> List[Dict]:
    # 1) JSON：找 list[dict]
    rows = _find_rows(data)
    if rows is not None:
        out: List[Dict] = []
        for d in rows:
            out.append({
                "name_en": _clean(_pick(d, ["name","EnglishName","Name_en","English Name"])),
                "addr_en": _clean(_pick(d, ["address","EnglishAddress","Address_en","English Address"])),
                "phone":   _clean(_pick(d, ["phone","Phone","Tel","Telephone"])),
                "rooms":   _to_int(_pick(d, ["room","RoomCount","Rooms"])),
            })
        return out
    # 2) CSV
    csv_rows = _parse_hotels_csv(str(data), lang="en")
    if csv_rows is not None:
        return csv_rows
    # 3) HTML
    return _parse_hotels_html(str(data), lang="en")
