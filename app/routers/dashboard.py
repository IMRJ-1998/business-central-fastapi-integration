from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.bc_client import BusinessCentralClient
from .auth import current_user

router = APIRouter()

@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    client = BusinessCentralClient(db)
    health = await client.health_check()
    items = await client.get_items() if health.ok else None
    rows = items.data.get("value", []) if items and items.ok and isinstance(items.data, dict) else []
    from ..main import templates
    return templates.TemplateResponse(
        request, "dashboard.html",
        {"user": user, "health": health, "items": rows[:20], "item_count": len(rows)}
    )
