"""add scatter chart columns

Revision ID: 0cd9370c096d
Revises: 3cbca27c3272
Create Date: 2026-10-02 15:17:12.431258
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0cd9370c096d"
down_revision: Union[str, Sequence[str], None] = "3cbca27c3272"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "charts",
        sa.Column(
            "x_column",
            sa.String(length=255),
            nullable=True
        )
    )

    op.add_column(
        "charts",
        sa.Column(
            "y_column",
            sa.String(length=255),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column(
        "charts",
        "y_column"
    )

    op.drop_column(
        "charts",
        "x_column"
    )