from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Chart(Base):
    __tablename__ = "charts"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    chart_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    dashboard_id: Mapped[int] = mapped_column(
        ForeignKey(
            "dashboards.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    dataset_id: Mapped[int] = mapped_column(
    ForeignKey(
        "datasets.id",
        ondelete="CASCADE"
    ),
    index=True
)

    group_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    operation: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    column: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )