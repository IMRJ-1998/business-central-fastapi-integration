import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import Base, SessionLocal, engine
from .models import User
from .security import hash_password
from .routers import auth, dashboard, admin

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(
                username="admin",
                password_hash=hash_password("AdminPassword123!"),
                role="admin",
                is_active=True,
            ))
            db.commit()
    finally:
        db.close()
    yield

app = FastAPI(
    title="Business Central Integration Dashboard",
    version="2.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(admin.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
