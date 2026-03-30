"""add_task_statuses_table

Revision ID: b51aac07fd4f
Revises: f0b90ecb49e3
Create Date: 2026-03-22 14:55:46.938550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b51aac07fd4f'
down_revision: Union[str, None] = 'f0b90ecb49e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
