from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="viewer", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

class SystemConfig(Base):
    __tablename__ = "system_config"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    bc_api_base_url: Mapped[str] = mapped_column(String(1000), default="")
    bc_auth_type: Mapped[str] = mapped_column(String(30), default="entra_id")
    bc_company_id: Mapped[str] = mapped_column(String(200), default="")

    entra_tenant_id: Mapped[str] = mapped_column(String(300), default="")
    entra_client_id: Mapped[str] = mapped_column(String(300), default="")
    entra_client_secret: Mapped[str] = mapped_column(String(1000), default="")
    entra_scope: Mapped[str] = mapped_column(
        String(1000), default="https://api.businesscentral.dynamics.com/.default"
    )

    basic_username: Mapped[str] = mapped_column(String(300), default="")
    basic_password: Mapped[str] = mapped_column(String(1000), default="")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
