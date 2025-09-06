
from fastapi import APIRouter, Request, Form, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import uuid
import bcrypt
from typing import Optional

from Database import Database

router = APIRouter()

@router.post("/signup")
def signup(email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    db = Database()
    if db.new_user(name, email, password, "user"):
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")
    return JSONResponse({"message": "Tài khoản tạo thành công"})

@router.post("/signin")
def signin(email: str = Form(...), password: str = Form(...)):
    db = Database()
    email = email.strip().lower()
    row = db.fetchone("SELECT id, pass, name FROM users WHERE email = %s;", [email])
    if not row or not bcrypt.checkpw(password.encode(), row[1]):
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không dúng")

    username = row[2]
    token = str(uuid.uuid4())
    
    db.execute("INSERT INTO refresh_tokens (uuid, user_id, token_hash, expires_at) VALUES (%s, %s, %s, %s);",
               [str(uuid.uuid4()), row[0], token, "2099-12-31 23:59:59"])
    
    return JSONResponse({
        "username": username,
        "access_token": token
    })


@router.post("/signout")
def signout(request: Request):
    db = Database()
    session_id = request.cookies.get("session_id")

    if session_id:
        # Revoke token trong DB
        db.execute("UPDATE refresh_tokens SET revoked = TRUE WHERE token_hash = %s;", [session_id])

    db.close()

    # Trả JSON thay vì redirect
    response = JSONResponse({"detail": "Signed out successfully"})
    response.delete_cookie("session_id")  # xóa cookie session
    return response