"""add dataset_id to charts

Revision ID: 0690d1d5aaf9
Revises: 4ff542429f53
Create Date: 2026-09-30 19:17:06.638577

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0690d1d5aaf9"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "4ff542429f53"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "charts",
        sa.Column(
            "dataset_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.execute(
        """
        UPDATE charts
        SET dataset_id = 11
        WHERE id = 1
        """
    )

    op.alter_column(
        "charts",
        "dataset_id",
        nullable=False
    )

    op.create_index(
        op.f("ix_charts_dataset_id"),
        "charts",
        ["dataset_id"],
        unique=False
    )

    op.create_foreign_key(
        "charts_dataset_id_fkey",
        "charts",
        "datasets",
        ["dataset_id"],
        ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "charts_dataset_id_fkey",
        "charts",
        type_="foreignkey"
    )

    op.drop_index(
        op.f("ix_charts_dataset_id"),
        table_name="charts"
    )

    op.drop_column(
        "charts",
        "dataset_id"
    )