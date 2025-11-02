# week3/
#  task1/
#    main.py          # 進入點：抓、解析、合併、輸出
#    fetchers.py      # 網路抓取＋JSON 嘗試解析
#    parsers.py       # 解析 CH/EN 結構，抽取欄位
#    merger.py        # 中英資料對齊與合併
#    exporters.py     # 輸出 CSV（欄位順序、編碼）
#    utils.py         # 共用：電話/數字正規化、行政區擷取、log
#    README.md        # 執行說明、假設、已知限制
#  hotels.csv         # 程式跑完自動生成
#  districts.csv      # 程式跑完自動生成

from pathlib import Path
from fetchers import fetch_text, try_parse_json
from parsers import parse_hotels_ch, parse_hotels_en
from merger import merge
from exporters import write_hotels_csv, write_districts_csv

CH_URL = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-ch"
EN_URL = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-en"

def main():
    root = Path(__file__).resolve().parents[1]
    out_hotels = root / "hotels.csv"
    out_districts = root / "districts.csv"

    ch_text = fetch_text(CH_URL)
    en_text = fetch_text(EN_URL)

    ch_data = try_parse_json(ch_text) or ch_text
    en_data = try_parse_json(en_text) or en_text

    ch_list = parse_hotels_ch(ch_data)
    en_list = parse_hotels_en(en_data)
    
    records = merge(ch_list, en_list)

    write_hotels_csv(records, out_hotels)
    write_districts_csv(records, out_districts)

if __name__ == "__main__":
    main()
