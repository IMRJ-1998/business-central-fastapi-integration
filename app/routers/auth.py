import os
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..security import COOKIE_NAME, create_access_token, decode_access_token, verify_password

router = APIRouter()

def current_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user = db.get(User, int(payload["sub"]))
        return user if user and user.is_active else None
    except Exception:
        return None

@router.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    if current_user(request, db):
        return RedirectResponse("/", status_code=303)
    from ..main import templates
    return templates.TemplateResponse(request, "login.html", {"error": None})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        from ..main import templates
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid username or password."}, status_code=401)
    token = create_access_token(user.id, user.username, user.role)
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        COOKIE_NAME, token, httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite="lax", max_age=60 * 60 * 8, path="/"
    )
    return response

@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(COOKIE_NAME, path="/")
    return response
