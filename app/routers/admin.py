from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..config_manager import get_config
from ..database import get_db
from ..models import User
from ..schemas import BCConfigUpdate
from ..security import hash_password
from ..services.bc_client import BusinessCentralClient
from .auth import current_user

router = APIRouter(prefix="/admin")

def admin_user(request: Request, db: Session):
    user = current_user(request, db)
    return user if user and user.role == "admin" else None

@router.get("")
async def admin_home(request: Request, db: Session = Depends(get_db)):
    user = admin_user(request, db)
    if not user:
        return RedirectResponse("/" if current_user(request, db) else "/login", status_code=303)
    return RedirectResponse("/admin/users", status_code=303)

@router.get("/users")
async def users_page(request: Request, db: Session = Depends(get_db)):
    user = admin_user(request, db)
    if not user:
        return RedirectResponse("/" if current_user(request, db) else "/login", status_code=303)
    from ..main import templates
    return templates.TemplateResponse(
        request, "admin_users.html",
        {"user": user, "users": db.query(User).order_by(User.id).all()}
    )

@router.post("/users")
async def create_user(
    request: Request, username: str = Form(...), password: str = Form(...),
    role: str = Form("viewer"), db: Session = Depends(get_db)
):
    admin = admin_user(request, db)
    if not admin:
        return RedirectResponse("/login", status_code=303)
    if role not in {"admin", "viewer"} or len(password) < 10:
        return RedirectResponse("/admin/users?error=invalid", status_code=303)
    if db.query(User).filter(User.username == username).first():
        return RedirectResponse("/admin/users?error=exists", status_code=303)
    db.add(User(username=username, password_hash=hash_password(password), role=role))
    db.commit()
    return RedirectResponse("/admin/users", status_code=303)

@router.post("/users/{user_id}/delete")
async def delete_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    admin = admin_user(request, db)
    if not admin:
        return RedirectResponse("/login", status_code=303)
    target = db.get(User, user_id)
    if target and target.id != admin.id:
        db.delete(target)
        db.commit()
    return RedirectResponse("/admin/users", status_code=303)

@router.get("/settings")
async def settings_page(request: Request, db: Session = Depends(get_db)):
    user = admin_user(request, db)
    if not user:
        return RedirectResponse("/" if current_user(request, db) else "/login", status_code=303)
    from ..main import templates
    return templates.TemplateResponse(
        request, "admin_settings.html",
        {"user": user, "config": get_config(db)}
    )

@router.post("/settings")
async def save_settings(
    request: Request,
    bc_api_base_url: str = Form(...), bc_auth_type: str = Form(...),
    bc_company_id: str = Form(""),
    entra_tenant_id: str = Form(""), entra_client_id: str = Form(""),
    entra_client_secret: str = Form(""),
    entra_scope: str = Form("https://api.businesscentral.dynamics.com/.default"),
    basic_username: str = Form(""), basic_password: str = Form(""),
    db: Session = Depends(get_db)
):
    user = admin_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    payload = BCConfigUpdate(
        bc_api_base_url=bc_api_base_url, bc_auth_type=bc_auth_type,
        bc_company_id=bc_company_id, entra_tenant_id=entra_tenant_id,
        entra_client_id=entra_client_id, entra_client_secret=entra_client_secret,
        entra_scope=entra_scope, basic_username=basic_username,
        basic_password=basic_password
    )
    config = get_config(db)
    for field, value in payload.model_dump().items():
        setattr(config, field, value)
    db.commit()
    return RedirectResponse("/admin/settings?saved=1", status_code=303)

@router.post("/settings/test")
async def test_connection(request: Request, db: Session = Depends(get_db)):
    user = admin_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    result = await BusinessCentralClient(db).health_check()
    from ..main import templates
    return templates.TemplateResponse(
        request, "admin_settings.html",
        {"user": user, "config": get_config(db), "test_result": result}
    )
