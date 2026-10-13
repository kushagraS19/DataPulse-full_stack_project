"""add dataset to dashboards

Revision ID: b8bbb0627995
Revises: 37828a29968c
Create Date: 2026-10-06 23:51:40.862896

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8bbb0627995"
down_revision: Union[str, Sequence[str], None] = "37828a29968c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the column temporarily as nullable so existing dashboards
    # can remain in the database while we establish their dataset mapping.
    op.add_column(
        "dashboards",
        sa.Column("dataset_id", sa.Integer(), nullable=True),
    )

    # NOTE:
    # Existing dashboard rows must be mapped to datasets before
    # dataset_id can safely become NOT NULL.
    #
    # We intentionally do NOT add the foreign key or unique constraint
    # yet because existing dashboard records have no dataset_id values.
    #
    # These constraints will be added after the existing data has been
    # mapped safely.


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("dashboards", "dataset_id")