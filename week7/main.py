# 啟動 FastAPI 應用程式，終端機輸入：uvicorn main:app --reload

from fastapi import FastAPI, Request, Form          # FastAPI:建立web app的主物件；Request:讓Jinja2模板可以拿到請求物件；Form:從HTML form抽出欄位值
from fastapi.responses import RedirectResponse                  # 用來產生「重新導向」的 HTTP 回應
from fastapi.staticfiles import StaticFiles                     # 專門用來「服務靜態檔案」的 ASGI app
from fastapi.templating import Jinja2Templates                  # 是FastAPI 包好的「Jinja2 模板管理器」
from starlette.middleware.sessions import SessionMiddleware     # Middleware（中介層），負責處理「Session」用來記錄登入狀態
import mysql.connector # 連接資料庫
from pydantic import BaseModel # 資料驗證，使用 Pydantic 的 BaseModel 

import os                      
from dotenv import load_dotenv 
load_dotenv()

# 用FastAPI這個類別，生出一個應用程式物件，名稱是app
# FastAPI=蓋網站的模板 / app=蓋出來的這個網站實體
app = FastAPI()

# 繼承 BaseModel
class UpdateMember(BaseModel):  
    name: str

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

    # 渲染頁面，把 member_name 這個變數以及messages 列表，傳給 member.html (即可在會員頁透過程式碼顯示會員名稱)
    return templates.TemplateResponse(
        "member.html",
        {
            "request": request,
            "member_name": member_name, # 傳遞會員名稱，左邊是 HTML 用的變數名，右邊是 Python 變數
            }
        )

# 查詢會員ID
@app.get("/api/member/{member_id}")
def get_member(request: Request, member_id: int):
    conn = get_db_connection() # 取得資料庫連線
    if conn is None:
        return RedirectResponse("/ohoh?msg=系統連線錯誤", status_code=303)  
    
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id,name,email FROM member WHERE id = %s"
        cursor.execute(query, (member_id,))
        member = cursor.fetchone() # 只取一筆

        # 記錄誰查詢會員資訊
        if member:
            # 誰在查? 從session拿資料
            searcher_id = request.session.get("MEMBER_ID")

            # 只有有登入且不是查自己的時候紀錄，!= 的判斷可使查自己不會被紀錄
            if searcher_id and searcher_id != member_id:
                try:
                    # 寫入 query_log 表格
                    insert_query = "INSERT INTO query_log (member_id, searcher_id) VALUES (%s, %s)"
                    cursor.execute(insert_query, (member_id, searcher_id))
                    conn.commit()
                except:
                    pass

        if member:
            return {"data": member}

        else:
            return { "data":None}

    finally: # 確保連線關閉
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

# 更新名字
@app.patch("/api/member")
def update_member(request: Request, update_data: UpdateMember):
    # 檢查是否登入
    member_id = request.session.get("MEMBER_ID")
    if not member_id:
        # JSON格式回傳錯誤訊息
        return {"error": True}

    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        query = "UPDATE member SET name = %s WHERE id = %s"
        
        # 執行:將新名字和會員ID填入
        cursor.execute(query, (update_data.name, member_id))

        # 同步更新 Session 裡的會員名稱
        request.session["MEMBER_NAME"] = update_data.name

        conn.commit()
        # 更新成功
        return {"ok": True}
    
    except mysql.connector.Error as err:
        return{"error": True}
    
    finally: #確保連線關閉
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

# 取得查詢紀錄 API
@app.get("/api/query-log")
def get_query_log(request: Request):
    # 檢查是否登入
    member_id = request.session.get("MEMBER_ID")
    if not member_id:
        return {"error": True}

    conn = get_db_connection()
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)
        
        # SQL 
        # 使用 INNER JOIN 把 member 表格併一起，拿得到查詢者的名字 (m.name)
        # WHERE q.member_id = %s: 找出「誰查了我」
        # ORDER BY q.time DESC: 最新的在上面
        # LIMIT 10: 只取 10 筆
        query = """
        SELECT m.name, q.time 
        FROM query_log AS q
        INNER JOIN member AS m ON q.searcher_id = m.id
        WHERE q.member_id = %s
        ORDER BY q.time DESC
        LIMIT 10
        """
        
        cursor.execute(query, (member_id,))
        logs = cursor.fetchall() # 取出所有符合的資料
        
        # 回傳資料
        return {"data": logs}

    except mysql.connector.Error as err:
        print(f"查詢紀錄失敗: {err}")
        return {"error": True}

    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

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
