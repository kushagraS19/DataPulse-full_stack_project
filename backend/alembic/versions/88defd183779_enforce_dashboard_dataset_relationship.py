"""enforce dashboard dataset relationship

Revision ID: 88defd183779
Revises: b8bbb0627995
Create Date: 2026-10-07 00:06:19.445737

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "88defd183779"
down_revision: Union[str, Sequence[str], None] = "b8bbb0627995"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "dashboards",
        "dataset_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_index(
        "ix_dashboards_dataset_id",
        "dashboards",
        ["dataset_id"],
        unique=True,
    )

    op.create_foreign_key(
        "fk_dashboards_dataset_id",
        "dashboards",
        "datasets",
        ["dataset_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_dashboards_dataset_id",
        "dashboards",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_dashboards_dataset_id",
        table_name="dashboards",
    )

    op.alter_column(
        "dashboards",
        "dataset_id",
        existing_type=sa.Integer(),
        nullable=True,
    )