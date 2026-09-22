from app.models.base import Base

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

class User (Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(100))

    email : Mapped[int] = mapped_column(
        String(225),
        unique=True,
        index=True
    )

    password_hash : Mapped[str] = mapped_column(
        String(225)
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime,
        default= datetime.utcnow
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="admin",
        server_default="admin",
        nullable=False
    )

    token_version: Mapped[int] = mapped_column(
        default=0,
        server_default="0",
        nullable=False
    )
    email_verified: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        nullable=False
    )