# 啟動 FastAPI 應用程式，終端機輸入：uvicorn main:app --reload

from fastapi import FastAPI, Request, Form          # FastAPI:建立web app的主物件；Request:讓Jinja2模板可以拿到請求物件；Form:從HTML form抽出欄位值
from fastapi.responses import RedirectResponse                  # 用來產生「重新導向」的 HTTP 回應
from fastapi.staticfiles import StaticFiles                     # 專門用來「服務靜態檔案」的 ASGI app
from fastapi.templating import Jinja2Templates                  # 是FastAPI 包好的「Jinja2 模板管理器」
from starlette.middleware.sessions import SessionMiddleware     # Middleware（中介層），負責處理「Session」用來記錄登入狀態
import mysql.connector # 連接資料庫

import os                      
from dotenv import load_dotenv 
load_dotenv()

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

# 資料庫連線設定
DB_CONFIG = {
    "user": os.getenv("DB_USER"), # 從環境變數.env讀取帳號
    "password":os.getenv("DB_PASSWORD"), # 從環境變數.env讀取密碼
    "host": "localhost",
    "database": "website", # 資料庫名稱是 website
    "port": 3306 # 3306 是 MySQL 資料庫伺服器預設的標準連線埠 (Port Number)
}

# 資料庫連線函式
def get_db_connection():
    try:
        # 使用設定檔建立一個新的連線
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"資料庫連線錯誤: {err}")
        return None

# 註冊帳號
@app.post("/signup")
def signup(
    request: Request,
    name: str = Form(""), # str = 告訴 FastAPI name 這個欄位預期收到『純文字』資料
    email: str = Form(""),
    password: str = Form(""),
):
    if not name or not email or not password:
        # 後端防護
        return RedirectResponse("/ohoh?msg=請輸入完整資訊", status_code=303)

    conn = get_db_connection()
    if conn is None:
        return RedirectResponse("/ohoh?msg=系統連線錯誤", status_code=303)

    cursor = None

    try:
        cursor = conn.cursor()
        # 2. 檢查電子郵件是否重複 (Task 2)
        cursor.execute("SELECT id FROM member WHERE email = %s", (email,))
        member = cursor.fetchone()

        if member:
            # 2.i. 電子郵件重複 (Task 2)
            return RedirectResponse("/ohoh?msg=重複的電子郵件", status_code=303)
        
        # 3. 註冊成功，寫入資料庫 (Task 2)
        insert_query = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (name, email, password))
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"資料庫操作錯誤: {err}")
        return RedirectResponse("/ohoh?msg=資料庫寫入失敗", status_code=303)

    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

    # 4. 導向首頁 (Task 2, 52)
    return RedirectResponse("/", status_code=303)


# 首頁 / 顯示註冊&登入欄位
@app.get("/") # GET 方法：當有瀏覽器對 GET/發送請求時，請呼叫下面這個函式 home 來處理
def home(request: Request):
    # 用 SignupForm.html 當模板，傳入 request 給 Jinja2 使用
    return templates.TemplateResponse("SignupForm.html", {"request": request}) 

# 驗證登入
@app.post("/login")
def login(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
):
    if not email or not password:
        # 信箱或密碼沒有填入時，顯示請輸入信箱和密碼
        return RedirectResponse("/ohoh?msg=請輸入信箱和密碼", status_code=303)
    
    conn = get_db_connection() # 1.取得資料庫連線
    if conn is None:
        return RedirectResponse("/ohoh?msg=系統連線錯誤", status_code=303)  
    
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True) # 使用 dictionary=True 讓結果以字典形式返回，方便取值
        # 2.檢查資料庫是否存在 email/password 配對
        query = "SELECT id,name,email FROM member WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        member = cursor.fetchone() # 只取一筆

        if member:
            # 3.登入成功，紀錄 member id,name,email 到Session
            request.session["LOGGED_IN"] = True
            request.session["MEMBER_ID"] = member["id"]
            request.session["MEMBER_NAME"] = member["name"] # 把資料庫查到的 name 存進 Session，取名為 "MEMBER_NAME"
            request.session["MEMBER_EMAIL"] = member["email"]
            # 導向會員頁
            return RedirectResponse("/member", status_code=303)
        
        else:
            # 4. 登入失敗
            return RedirectResponse("/ohoh?msg=電子郵件或密碼錯誤", status_code=303)
        
    except mysql.connector.Error as err:
        print(f"資料庫操作錯誤: {err}")
        return RedirectResponse("/ohoh?msg=資料庫查詢失敗", status_code=303)

    finally:
        # 5. 確保連線關閉
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

# 會員成功頁+Session驗證
@app.get("/member")
def member(request: Request):
    # 檢查登入狀態
    if not request.session.get("LOGGED_IN"): # 讀當前 session 裡的登入狀態
        # 未登入，強制導向首頁
        return RedirectResponse("/", status_code=303)

    # 從 Session 拿出剛剛存的 "MEMBER_NAME"
    member_name = request.session.get("MEMBER_NAME", "會員")

    # 取得 ID 用來判斷是否為自己的留言
    current_member_id = request.session.get("MEMBER_ID") 

    # 撈取留言邏輯
    conn = get_db_connection()
    if conn is None:
        # 如果連線失敗，直接導向錯誤頁面
        return RedirectResponse("/ohoh?msg=系統連線錯誤",status_code=303)

    # 連線成功才宣告 messages 並開始查詢
    messages = []

    cursor = None

    try:
        # 使用 dictionary=True 讓結果以字典形式返回，讓撈出來的每一筆資料變成 Python 字典 (例如: {"name": "abc", "content": "你好！"})
        cursor = conn.cursor(dictionary=True)
        
        # SQL 用 INNER JOIN 把「留言表」和「會員表」連起來，同時拿到「留言內容」和「是誰留的」
        # 按照 time 降序排列 (DESC) 顯示最新的留言
        query = """
        SELECT 
            m.id, m.content, m.member_id, 
            mb.name AS member_name 
        FROM message AS m 
        INNER JOIN member AS mb ON m.member_id = mb.id 
        ORDER BY m.time DESC
        """
        cursor.execute(query)

        # 取出所有結果
        messages = cursor.fetchall()

        # 為每則留言添加一個 flag，標記是否為當前會員的留言
        for message in messages:
            # 如果留言作者的 ID 等於當前登入者的 ID，則設為 True
            # 拿出每一則留言，看它的 member_id（作者 ID）拿去跟 current_member_id（登入者 ID）做比對
            # 如果號碼一樣：在這則留言上貼一個標籤 is_my_message = True / 號碼不一樣：貼上標籤 is_my_message = False
            # ==（等於）的時候，電腦會自動回答「對 (True)」或「錯 (False)」
            message["is_my_message"] = (message["member_id"] == current_member_id)

    except mysql.connector.Error as err:
        print(f"留言查詢錯誤: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

    # 渲染頁面，把 member_name 這個變數以及messages 列表，傳給 member.html (即可在會員頁透過程式碼顯示會員名稱)
    return templates.TemplateResponse(
        "member.html",
        {
            "request": request,
            "member_name": member_name, # 傳遞會員名稱，左邊是 HTML 用的變數名，右邊是 Python 變數
            "messages":messages # 傳遞留言列表（把資料傳給前端）
            }
        )


# 留言功能
@app.post("/createMessage")
def create_message(request: Request, content: str = Form("")):
    # 1. 檢查是否登入
    # 註：雖然 /member 頁面會檢查登入，但為了防止直接發送 POST 請求，這裡做雙重檢查
    member_id = request.session.get("MEMBER_ID")
    if not member_id:
        return RedirectResponse("/", status_code=303)

    # 2. 檢查留言內容
    if not content or content.strip() == "":
        # 如果內容為空，導回 member 頁面
        return RedirectResponse("/member", status_code=303)

    conn = get_db_connection()
    if conn is None:
        return RedirectResponse("/ohoh?msg=系統連線錯誤", status_code=303)

    cursor = None

    try:
        cursor = conn.cursor()
        # 3. 寫入 message 表格
        insert_query = "INSERT INTO message (member_id, content) VALUES (%s, %s)"
        cursor.execute(insert_query, (member_id, content))
        conn.commit()

    except mysql.connector.Error as err:
        print(f"留言寫入錯誤: {err}")
        # 即使寫入失敗，仍導回會員頁，但可以在 /ohoh 顯示更詳細錯誤
        return RedirectResponse("/ohoh?msg=留言寫入失敗", status_code=303)

    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

    # 4. 導回 Member Page
    return RedirectResponse("/member", status_code=303)

# 刪除留言
@app.post("/deleteMessage")
# FastAPI 從 HTML 表單中把隱藏的 message_id 抓出來，Form(...) 表示這個變數是從前端表單裡拿出來的
def delete_message(request: Request, message_id: int = Form(...)):
    # 1. 檢查是否登入，靠讀取 message_id 來決定要刪除資料庫裡的哪一行
    member_id = request.session.get("MEMBER_ID")
    if not member_id:
        # 未登入者不能刪除
        return RedirectResponse("/", status_code=303)

    conn = get_db_connection()
    if conn is None:
        return RedirectResponse("/ohoh?msg=系統連線錯誤", status_code=303)

    cursor = None

    try:
        cursor = conn.cursor()
        # 2. 執行安全刪除
        # SQL 指令：刪除 message 表格中 id 符合的那一筆，確保刪除的 message_id 屬於當前的 member_id
        delete_query = """
        DELETE FROM message 
        WHERE id = %s AND member_id = %s
        """
        # 執行刪除動作 (傳入 message_id 和 member_id 做雙重確認)
        cursor.execute(delete_query, (message_id, member_id))
        conn.commit() # 確認執行，真正把資料從資料庫刪除

    except mysql.connector.Error as err:
        print(f"留言刪除錯誤: {err}")
        return RedirectResponse("/ohoh?msg=留言刪除失敗", status_code=303)

    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

    # 3. 導回 Member Page
    return RedirectResponse("/member", status_code=303)

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
    # 清除所有與登入相關的 Session 資訊
    if "LOGGED_IN" in request.session:
        del request.session["LOGGED_IN"]
    if "MEMBER_ID" in request.session: # 清除會員 ID
        del request.session["MEMBER_ID"]
    if "MEMBER_NAME" in request.session: # 清除會員名稱
        del request.session["MEMBER_NAME"]
    if "MEMBER_EMAIL" in request.session: 
        del request.session["MEMBER_EMAIL"] # 清除 email
    
    # 導向首頁
    return RedirectResponse("/", status_code=303)

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
