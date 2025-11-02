# week3/
#  task2/
#    main.py          # 進入點：抓前三頁 → 抓每篇 → 輸出 CSV
#    ptt.py           # 抓頁面、解析清單/內文、工具函式
#    exporters.py     # 輸出 CSV
#  articles.csv       # 程式跑完自動生成


from pathlib import Path
from ptt import fetch_list_page, find_prev_page, parse_list_items, fetch_article_time
from exporters import write_articles_csv

BASE = "https://www.ptt.cc"

def crawl_first_n_pages(board: str, pages: int = 3):
    url = f"{BASE}/bbs/{board}/index.html"
    all_items = []

    for _ in range(pages):
        html = fetch_list_page(url)
        items = parse_list_items(html)
        # 依序補上發文時間（需要進到文章頁）
        for it in items:
            it["PublishTime"] = fetch_article_time(BASE + it["href"]) if it.get("href") else ""
            all_items.append({
                "ArticleTitle": it["title"],
                "LikeCount": it["nrec"],
                "PublishTime": it["PublishTime"],
            })
        prev = find_prev_page(html)
        if not prev: break
        url = BASE + prev

    return all_items

def main():
    root = Path(__file__).resolve().parents[1]
    out_csv = root / "articles.csv"

    records = crawl_first_n_pages("Steam", pages=3)
    write_articles_csv(records, out_csv)

if __name__ == "__main__":
    main()
