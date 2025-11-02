import csv
from typing import List, Dict

HEADER = ["ArticleTitle", "LikeCount", "PublishTime"]

def write_articles_csv(records: List[Dict], path):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k, "") for k in HEADER})
