"""Add dob and gender fields to User model

Revision ID: df9473d206bb
Revises: b06ef3f17137
Create Date: 2025-06-27 20:39:34.253387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df9473d206bb'
down_revision: Union[str, None] = 'b06ef3f17137'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('dob', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'gender')
    op.drop_column('users', 'dob')
