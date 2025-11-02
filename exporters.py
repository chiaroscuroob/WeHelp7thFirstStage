import csv
from typing import Dict, List
from utils import extract_district

HOTELS_HEADER = ["ChineseName","EnglishName","ChineseAddress","EnglishAddress","Phone","RoomCount"]
DISTRICTS_HEADER = ["DistrictName","HotelCount","RoomCount"]

def write_hotels_csv(records: List[Dict], path):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HOTELS_HEADER)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k,"") for k in HOTELS_HEADER})

def write_districts_csv(records: List[Dict], path):
    agg = {}
    for r in records:
        dist = extract_district(r.get("ChineseAddress",""))
        if not dist: continue
        agg.setdefault(dist, {"HotelCount":0, "RoomCount":0})
        agg[dist]["HotelCount"] += 1
        agg[dist]["RoomCount"] += int(r.get("RoomCount") or 0)

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(DISTRICTS_HEADER)
        for dist, v in agg.items():
            w.writerow([dist, v["HotelCount"], v["RoomCount"]])
