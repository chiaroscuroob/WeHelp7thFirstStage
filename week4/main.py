import requests
from fastapi import FastAPI, Request, Form          # FastAPI:建立web app的主物件；Request:讓Jinja2模板可以拿到請求物件；Form:從HTML form抽出欄位值
from fastapi.responses import RedirectResponse                  # 用來產生「重新導向」的 HTTP 回應
from fastapi.staticfiles import StaticFiles                     # 專門用來「服務靜態檔案」的 ASGI app
from fastapi.templating import Jinja2Templates                  # 是FastAPI 包好的「Jinja2 模板管理器」
from starlette.middleware.sessions import SessionMiddleware     # Middleware（中介層），負責處理「Session」用來記錄登入狀態

# 用FastAPI這個類別，生出一個應用程式物件，名稱是app
# FastAPI=蓋網站的模板 / app=蓋出來的這個網站實體
app = FastAPI()

# Session 設定，用來記錄登入狀態
app.add_middleware(SessionMiddleware, secret_key="a-very-secret-key")

# 靜態檔(CSS&JS)與模板設定
# 只要使用者請求的 URL 是 /static/... 開頭，就去專案的 static/ 資料夾裡找對應檔案
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML 模板都放在 templates/ 資料夾裡
templates = Jinja2Templates("templates")

# task4 飯店資料庫
URL_CH = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-ch"
URL_EN = "https://resources-wehelp-taiwan-b986132eca78c0b5eeb736fc03240c2ff8b7116.gitlab.io/hotels-en"

list_ch = requests.get(URL_CH).json()["list"]
list_en = requests.get(URL_EN).json()["list"]

# 把中、英資料各自變成 dict，用 _id 當 key
hotels_ch_by_id = {item["_id"]: item for item in list_ch}
hotels_en_by_id = {item["_id"]: item for item in list_en}

# 整理成 task4 規範結構
HOTELS = {
    hid: {
        "name_zh": ch.get("旅宿名稱", ""),
        "name_en": hotels_en_by_id.get(hid, {}).get("hotel name", ""),
        "phone": ch.get("電話或手機號碼", ""),
    }
    for hid, ch in hotels_ch_by_id.items()
}

# 首頁 / 顯示登入+飯店查詢表
@app.get("/") # GET 方法：當有瀏覽器對 GET/發送請求時，請呼叫下面這個函式 home 來處理
def home(request: Request):
    # 用 index.html 當模板，傳入 request 給 Jinja2 使用
    return templates.TemplateResponse("index.html", {"request": request}) 
    # ↑ 補充步驟
    # 1.找到 templates/index.html
    # 2.把傳進來的字典（context，例如 {"hotel": hotel}）塞進 Jinja2
    # 3.套用 {% if %}、{{ 變數 }} 等模板語法
    # 4.產生一個 HTML 回應物件回給 FastAPI

# 驗證登入
@app.post("/login")
def login(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
):
    if not email or not password:
        return RedirectResponse("/ohoh?msg=請輸入信箱和密碼", status_code=303)      
        # 信箱或密碼沒有填入時，顯示請輸入信箱和密碼
    if email == "abc@abc.com" and password == "abc":
        # 設定登入狀態
        request.session["LOGGED_IN"] = True
        # 信箱和密碼正確時，紀錄登入資訊
        return RedirectResponse("/member", status_code=303)
        
    return RedirectResponse("/ohoh?msg=信箱或密碼輸入錯誤", status_code=303)
    # 其他所有情況 = 輸入錯誤時

# 會員成功頁+Session驗證
@app.get("/member")
def member(request: Request):
    # 檢查登入狀態
    if not request.session.get("LOGGED_IN"): # 讀當前 session 裡的登入狀態
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("member.html", {"request": request})

# 錯誤頁
@app.get("/ohoh")
def error_page(request: Request, msg: str = "發生錯誤"):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": msg},
    )

# 登出
@app.get("/logout")
def logout(request: Request):
    request.session["LOGGED_IN"] = False
    return RedirectResponse("/", status_code=303)

# 查詢飯店
@app.get("/hotel/{hotel_id}")
def hotel_detail(request: Request, hotel_id: int):
    # 如果 hotel 有值 → hotel.html 裡的 {% if hotel %} 會走「有資料」
    # 如果 hotel 是 None → 模板走「查詢不到相關資料」
    hotel = HOTELS.get(hotel_id)
    return templates.TemplateResponse(
        "hotel.html",
        {"request": request, "hotel": hotel},
    )

# ----------------------------筆記----------------------------

# FastAPI
# → 生出 app，整個網站的主體（路由、middleware、static、模板全掛這裡）

# Request
# → 在每個路由函式裡，代表「這一次請求」的相關資訊（含 session），是模板需要的參數

# Form
# → 從 HTML form 裡抽 email / password，變成函式的參數

# RedirectResponse
# → 做登入/錯誤/登出的「導頁」行為（回傳 303 + Location header）

# StaticFiles
# → 讓 /static/... URL 可以送出真正的 CSS / JS 檔案

# Jinja2Templates
# → 把 .html 模板 + 變數 → 變成真正的 HTML 回應（支援 {{ }} & {% if %}）

# SessionMiddleware
# → 管理登入 session，用 Cookie 在不同請求之間記住使用者狀態
