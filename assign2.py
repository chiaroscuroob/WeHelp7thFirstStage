# WeHelp Week 2 - assign2.py
# 注意：不使用任何第三方套件、絕不更改現有程式碼

# ---------- Task 1 ----------
# 悟空固定 (0,0)；其餘座標與Task1圖示一致
POINTS = {
    "悟空":     ( 0,  0),
    "辛巴":     (-3,  3),
    "丁滿":     (-1,  4),
    "貝吉塔":   (-4, -1),
    "特南克斯": ( 1, -2),
    "弗利沙":   ( 4, -1),
}
# POINTS = {...}：指派（assignment）把右邊的資料結構賦值給變數 POINTS
# { ... }：字典（dict）常值。是一種「鍵 → 值」(key → value) 的對應表
# "<名字>": (<x>, <y>)：每一行是一個鍵值對；
# 鍵（key）是字串，例如 "悟空"
# 值（value）是元組（tuple），用括號 (...) 表示不可變序列，這裡是一對整數 (x, y)，代表 2D 座標

# 斜線用兩點定義
LINE_P1 = (-3, 5)
LINE_P2 = ( 5,-4)

# 為了穩定輸出順序，明確定義名字順序（與上方 dict 插入順序一致）
NAMES = ["悟空", "辛巴", "丁滿", "貝吉塔", "特南克斯", "弗利沙"]

# 用兩點定義直線，再用叉積符號判斷相對位置，回傳點在哪一側（>0、<0、=0）
def _side(p):
    """回傳點 p 在斜線哪一側：>0 一側、<0 另一側、=0在線上"""
    (x, y) = p
    (x1, y1), (x2, y2) = LINE_P1, LINE_P2
    v = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
    return 1 if v > 0 else (-1 if v < 0 else 0)

# Manhattan 算基本距離（符合水平/垂直移動規則）
def _manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# 基本距離 + 若分處兩側則額外 +2
def _dist(name_a, name_b):
    A, B = POINTS[name_a], POINTS[name_b]
    d = _manhattan(A, B)
    if _side(A) * _side(B) < 0:  # 在不同側 → 另加 2
        d += 2
    return d

def func1(name):
    if name not in POINTS:
        print(f"查無角色：{name}")
        return

    # 用固定順序 NAMES 產生距離清單，確保輸出順序穩定（避免 set / dict 無序造成的隨機列印順序）
    others = [(n, _dist(name, n)) for n in NAMES if n != name]

    # 找最小/最大距離
    dists = [d for _, d in others]
    dmin, dmax = min(dists), max(dists)

    # 挑出所有最近/最遠者（若同距離全部列出，順序依 NAMES）
    closest  = [n for (n, d) in others if d == dmin]
    farthest = [n for (n, d) in others if d == dmax]

    # 依題目格式印出
    print(f"最遠{ '、'.join(farthest) }；最近{ '、'.join(closest) }")

# Note: Never change existing code.
func1("辛巴")     # print 最遠弗利沙；最近丁滿、貝吉塔
func1("悟空")     # print 最遠丁滿、弗利沙；最近特南克斯
func1("弗利沙")   # print 最遠辛巴，最近特南克斯
func1("特南克斯") # print 最遠丁滿，最近悟空


# ---------- Task 2 ----------

# 規則：
# 1) 預約一筆一筆處理，前面的預約會占掉時段
# 2) 條件只允許：Field=Value、Field>=Value、Field<=Value
# 3) name 欄位只用 '='；r/c 欄位只用 '>=' 或 '<='
# 4) 在「此時段可用」的服務中，挑最貼近門檻者：
#    - op == ">="：選 v 最小但仍 >= 門檻
#    - op == "<="：選 v 最大但仍 <= 門檻
#    - 同值時以名稱字母序較小者
# 5) 無可用服務時印 "Sorry"

import re

# 跨呼叫狀態：name -> 已預約時段清單（每筆為 [start, end) 半開區間）
from typing import Dict, List, Tuple
# 紀錄每個服務已被預約的時段清單。使用半開區間方便判斷不重疊情況（[e1 <= s2] 或 [e2 <= s1] 視為不重疊
_BOOKED: Dict[str, List[Tuple[int, int]]] = {}

# 半開區間重疊判斷：尾接頭（例如 [8,9) 與 [9,10)）不算重疊，這樣才能「剛好接在後面」的預約成立
def _overlap(s1: int, e1: int, s2: int, e2: int) -> bool:
    return not (e1 <= s2 or e2 <= s1)
def _is_available(name: str, start: int, end: int) -> bool:
    slots = _BOOKED.get(name, [])
    return all(not _overlap(start, end, s, e) for s, e in slots)

# 成功挑到服務後，將此次時段記錄，影響之後的呼叫（符合「先來先佔」）
def _book(name: str, start: int, end: int) -> None:
    _BOOKED.setdefault(name, []).append((start, end))

# 只接受 name / r / c 三種欄位，且運算子僅 = / >= / <=
def _parse_criteria(criteria: str):
    m = re.match(r'^(name|r|c)\s*(=|>=|<=)\s*(.+)$', criteria.strip())
    if not m:
        # 題目不會給壞格式；保險起見讓它找不到任何服務
        return None, None, None
    field, op, raw = m.groups()
    value = raw.strip() if field == "name" else float(raw)
    return field, op, value

# 選服務
def _pick_service(candidates: list[dict], field: str, op: str, value):
    # 題目規範的操作合法性（保險防呆；題目本身不會亂給）
    if field == "name" and op != "=":
        return None
    if field in ("r", "c") and op == "=":
        return None

    if field == "name":
        return next((s for s in candidates if s["name"] == value), None)

    # r/c：先過濾符合不等式者
    def fit(s):
        v = float(s[field])
        return v >= value if op == ">=" else v <= value

    pool = [s for s in candidates if fit(s)]
    if not pool:
        return None

    # 依「最貼近門檻」排序；同值用名稱做穩定 tie-break
    if op == ">=":
        pool.sort(key=lambda s: (float(s[field]) - value, s["name"]))
    else:  # "<="
        pool.sort(key=lambda s: (-(float(s[field]) - value), s["name"]))
    return pool[0]

# 主流程
def func2(ss, start, end, criteria):
    field, op, value = _parse_criteria(criteria)
    # 篩出此時段可用的服務
    available = [s for s in ss if _is_available(s["name"], start, end)]
    chosen = _pick_service(available, field, op, value)

    if chosen is None:
        print("Sorry")
        return "Sorry"
    else:
        print(chosen["name"])
        _book(chosen["name"], start, end)  # 記錄預約，影響後續呼叫
        return chosen["name"]

# Note: Never change existing code.
services = [
    {"name": "S1", "r": 4.5, "c": 1000},
    {"name": "S2", "r": 3,   "c": 1200},
    {"name": "S3", "r": 3.8, "c": 800 },
]

func2(services, 15, 17, "c>=800")   # S3
func2(services, 11, 13, "r<=4")     # S3
func2(services, 10, 12, "name=S3")  # Sorry
func2(services, 15, 18, "r>=4.5")   # S1
func2(services, 16, 18, "r>=4")     # Sorry
func2(services, 13, 17, "name=S1")  # Sorry
func2(services, 8, 9,   "c<=1500")  # S2
func2(services, 8, 9, "c<=1500") # 要在符合條件且時段有空的 Services 中選 Best Match，舉個例子，如果最後多加一個測試 func2(services, 8, 9, "c<=1500"); 那麼要能印出 S1


# ---------- Task 3 ----------

def func3(index):
    # 循環差分：從 25 開始依序 -2, -3, +1, +2 重複
    diffs = [-2, -3, +1, +2] # [] 建立 list
    val = 25 #起點
    for i in range(index):  # 走 index 次（走幾步）；for...in 迴圈語法；range 會建立一個表示整數等差序列的物件
        val += diffs[i % 4] # % 取餘數
    print(val) # 把值顯示在螢幕上，主要給人看或除錯用
    return val # 把值傳回呼叫端，讓程式接著拿來運算

# i 在 for i in range(index) 裡會一路長大（0,1,2,3,4,5,6, ...）
# 但 diffs 只有索引 0..3。用 i % 4 取餘數，就能把任何 i 都摺回到 0~3 之間，形成週期性取值
# i = 0 → 0 % 4 = 0 → diffs[0] = -2
# i = 1 → 1 % 4 = 1 → diffs[1] = -3
# i = 2 → 2 % 4 = 2 → diffs[2] = +1
# i = 3 → 3 % 4 = 3 → diffs[3] = +2
# i = 4 → 4 % 4 = 0 → diffs[0] = -2（回到開頭）
# i = 5 → 5 % 4 = 1 → diffs[1] = -3
# 這樣就能讓差分序列 [-2, -3, +1, +2] 不斷重複，符合「循環差分」的規律

# Note: Never change existing code.
func3(1)   # print 23
func3(5)   # print 21
func3(10)  # print 16
func3(30)  # print 6


# ---------- Task 4 ----------

def func4(sp, stat, n):
    # 第一階段：Best Fit（能完整容納，剩餘座位越小越好，索引小者優先）
    # sp 每節可用座位數的 list
    # stat（字串，"0" 可用車廂、"1" 不可用車廂）
    # n（乘客數）
    best_idx = -1 # 目前最佳車廂索引；-1 表示還沒找到
    best_left = float("inf") # 目前最小「剩餘座位」；先放無限大作為比較基準
    for i, seats in enumerate(sp): # # 逐一走過每節車廂：i=索引、seats=該節可用座位
        if i >= len(stat) or stat[i] != "0": # 邊界/可用性檢查：超出 stat 長度或該節不可用("1")就跳過
            continue
        if seats >= n: # 只考慮「能完整容納 n 人」的車廂
            left = seats - n # 放下 n 人後的剩餘座位
            # 比較規則：剩餘座位更小者勝；若相同，索引更小者勝
            if left < best_left or (left == best_left and i < best_idx):
                best_left = left # 更新目前最好的剩餘座位
                best_idx = i # 更新目前最好的車廂索引

    if best_idx != -1: # 若第一階段找到合適車廂
        print(best_idx) # 依題意印出索引
        return best_idx # 並回傳索引

    # 第二階段：找最接近（車廂無法完整容納時，sp[i]-n 最大者；索引小者優先）
    fallback_idx = -1 # 備選方案索引；-1 表示還沒找到
    best_diff = -float("inf") # 最大的 sp[i]-n（通常是負數），先放負無限大
    for i, seats in enumerate(sp): # 再掃一次所有車廂（只看可用的）
        if i >= len(stat) or stat[i] != "0": # 同樣的可用性檢查
            continue
        diff = seats - n # 能容納差距：不足時會是負數，越接近 0 表示越「接近」能坐下
        # 比較規則：diff 更大者勝；若相同，索引更小者勝
        if diff > best_diff or (diff == best_diff and i < fallback_idx):
            best_diff = diff # 更新目前最接近的差距
            fallback_idx = i # 更新目前最接近的索引

    if fallback_idx != -1: # 若第二階段有找到候選
        print(fallback_idx) # 印出索引
        return fallback_idx # 並回傳索引

    # 全部車廂 stat == "1" 時，沒有車廂可使用時
    print("Sorry") # 依題意印出 "Sorry"
    return None # 沒有可用解，回傳 None

# Note: Never change existing code.
func4([3, 1, 5, 4, 3, 2], "101000", 2)  # print 5
func4([1, 0, 5, 1, 3], "10100", 4)      # print 4
func4([4, 6, 5, 8], "1000", 4)          # print 2

# 為什麼 best_idx = -1？
# best_idx 用來記錄「目前最佳的索引」
# 在還沒找到任何車廂之前，我們需要一個哨兵值（sentinel）表示「尚未找到」。-1 就是這個標記
# 進入迴圈後，只要遇到第一個候選，因為 left < inf，一定會更新成實際的索引
# 後面如果遇到平手（left == best_left），就用「索引較小者優先」打破平手：i < best_idx

# 為什麼 best_left = float("inf")？
# 在第一階段要找「剩餘座位 left = seats - n 最小」的車廂
# 如果一開始沒有任何基準，第一次比較會很尷尬：拿什麼去比？
# 把基準設成「無限大」有2個好處：
# 1.第一次命中一定贏
# 第一個符合 seats >= n 的車廂，它的 left 一定 < inf，所以會被收進來當新的最佳解
# 2.之後都能正常比較
# 有了第一個最佳解後，後面就能用「更小的 left 才取代」的規則一路比下去