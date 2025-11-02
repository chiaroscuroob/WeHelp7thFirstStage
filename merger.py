from typing import Dict, List
from utils import normalize_phone

def merge(ch_list: List[Dict], en_list: List[Dict]) -> List[Dict]:
    by_phone = {normalize_phone(c.get("phone","")): c for c in ch_list if c.get("phone")}
    used = set()
    out: List[Dict] = []

    # 先嘗試電話對應
    for en in en_list:
        key = normalize_phone(en.get("phone",""))
        if key and key in by_phone:
            ch = by_phone[key]; used.add(key)
            out.append(_compose(ch, en))
        else:
            out.append(_compose({}, en))  # 先放著，等下用索引補

    # 用索引把沒對上的補上
    ch_iter = iter([c for k,c in by_phone.items() if k not in used] + [c for c in ch_list if not normalize_phone(c.get("phone",""))])
    for i, r in enumerate(out):
        if r.get("_complete"): continue
        try:
            ch = next(ch_iter)
            out[i] = _compose(ch, r)
        except StopIteration:
            break

    for r in out: r.pop("_complete", None)
    return out

def _compose(ch: Dict, en: Dict) -> Dict:
    return {
        "ChineseName": ch.get("name_ch",""),
        "EnglishName": en.get("name_en",""),
        "ChineseAddress": ch.get("addr_ch",""),
        "EnglishAddress": en.get("addr_en",""),
        "Phone": ch.get("phone","") or en.get("phone",""),
        "RoomCount": int(ch.get("rooms") or en.get("rooms") or 0),
        "_complete": bool(ch and en),
    }
