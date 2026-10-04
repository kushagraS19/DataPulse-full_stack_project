"""add dataset metadata

Revision ID: 37828a29968c
Revises: 0cd9370c096d
Create Date: 2026-10-03 16:24:00.835941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37828a29968c'
down_revision: Union[str, Sequence[str], None] = '0cd9370c096d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'datasets',
        sa.Column(
            'row_count',
            sa.Integer(),
            nullable=False,
            server_default='0'
        )
    )

    op.add_column(
        'datasets',
        sa.Column(
            'column_count',
            sa.Integer(),
            nullable=False,
            server_default='0'
        )
    )

    op.add_column(
        'datasets',
        sa.Column(
            'file_size',
            sa.Integer(),
            nullable=False,
            server_default='0'
        )
    )

    op.alter_column(
        'datasets',
        'row_count',
        server_default=None
    )

    op.alter_column(
        'datasets',
        'column_count',
        server_default=None
    )

    op.alter_column(
        'datasets',
        'file_size',
        server_default=None
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('datasets', 'file_size')
    op.drop_column('datasets', 'column_count')
    op.drop_column('datasets', 'row_count')