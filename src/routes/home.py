from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import uuid
import bcrypt
import random
import datetime

from src.Database import Database

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = Database()
    session_id = request.cookies.get("session_id")

    user = None
    if session_id:
        row = db.fetchone("SELECT u.id, u.uuid, u.email, u.name, u.role "
                          "FROM users u JOIN refresh_tokens t ON u.id = t.user_id "
                          "WHERE t.token_hash = %s AND t.revoked = FALSE;", [session_id])
        if row:
            user = {
                "id": row[0],
                "uuid": row[1],
                "email": row[2],
                "name": row[3],
                "role": row[4],
            }
    db.close()
    return templates.TemplateResponse("home.html", {"request": request, "title": "Home", "user": user})


@router.post("/signup")
def signup(email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    db = Database()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    exists = db.fetchone("SELECT id FROM users WHERE email = %s;", [email])
    if exists:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    db.execute("INSERT INTO users (uuid, email, name, pass, role) VALUES (%s, %s, %s, %s, %s);",
               [str(uuid.uuid4()), email, name, hashed_password, "user"])
    db.close()
    return JSONResponse({"message": "Account created successfully"})

@router.post("/signin")
def signin(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    db = Database()
    row = db.fetchone("SELECT id, pass, name, uuid FROM users WHERE email = %s;", [email])

    if not row:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    stored_hash = row[1]
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = row[0]
    token = str(uuid.uuid4())

    # Random expiry 15-30 phút
    expiry_minutes = random.randint(15, 30)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expiry_minutes)

    db.execute(
        "INSERT INTO refresh_tokens (uuid, user_id, token_hash, expires_at) VALUES (%s, %s, %s, %s);",
        [str(uuid.uuid4()), user_id, token, expires_at]
    )
    db.close()

    response = RedirectResponse("/search", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="session_id",
        value=token,
        httponly=True,
        max_age=expiry_minutes * 60,
        expires=expiry_minutes * 60
    )
    print("???")
    return response


@router.post("/signout")
def signout(request: Request):
    db = Database()
    session_id = request.cookies.get("session_id")
    if session_id:
        db.execute("UPDATE refresh_tokens SET revoked = TRUE WHERE token_hash = %s;", [session_id])
    db.close()

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session_id")
    return response

@router.get("/search")
def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request, "title": "Home", "user": "user"})
    