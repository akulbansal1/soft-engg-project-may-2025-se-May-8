"""Change phone field from Integer to String

Revision ID: af191889e37c
Revises: df9473d206bb
Create Date: 2025-06-27 21:11:15.615636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af191889e37c'
down_revision: Union[str, None] = 'df9473d206bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('dob', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_new_id'), 'users_new', ['id'], unique=False)
    op.create_index(op.f('ix_users_new_phone'), 'users_new', ['phone'], unique=True)
    
    op.execute("INSERT INTO users_new (id, name, phone, dob, gender, is_active, created_at) SELECT id, name, CAST(phone AS TEXT), dob, gender, is_active, created_at FROM users")
    
    op.drop_table('users')
    
    op.rename_table('users_new', 'users')


def downgrade() -> None:
    op.create_table('users_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.Integer(), nullable=False),
        sa.Column('dob', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_new_id'), 'users_new', ['id'], unique=False)
    op.create_index(op.f('ix_users_new_phone'), 'users_new', ['phone'], unique=True)
    
    op.execute("INSERT INTO users_new (id, name, phone, dob, gender, is_active, created_at) SELECT id, name, CAST(phone AS INTEGER), dob, gender, is_active, created_at FROM users")
    
    op.drop_table('users')
    
    op.rename_table('users_new', 'users')
