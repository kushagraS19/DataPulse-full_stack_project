"""add dataset table name

Revision ID: 3cbca27c3272
Revises: 32927b6db5aa
Create Date: 2026-10-01 17:48:08.459074

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3cbca27c3272"
down_revision: Union[str, Sequence[str], None] = "32927b6db5aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the new column temporarily as nullable
    op.add_column(
        "datasets",
        sa.Column(
            "table_name",
            sa.String(length=255),
            nullable=True
        )
    )

    # Give existing datasets a temporary table name
    op.execute(
        """
        UPDATE datasets
        SET table_name = 'legacy_dataset_' || id
        WHERE table_name IS NULL
        """
    )

    # Make the column required
    op.alter_column(
        "datasets",
        "table_name",
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "datasets",
        "table_name"
    )