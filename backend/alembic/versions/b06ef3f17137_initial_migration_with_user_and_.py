"""Initial migration with User and PasskeyCredential tables

Revision ID: b06ef3f17137
Revises: 
Create Date: 2025-06-24 13:29:16.817468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b06ef3f17137'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('passkey_credentials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('credential_id', sa.String(), nullable=False),
    sa.Column('public_key', sa.Text(), nullable=False),
    sa.Column('sign_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_passkey_credentials_credential_id'), 'passkey_credentials', ['credential_id'], unique=True)
    op.create_index(op.f('ix_passkey_credentials_id'), 'passkey_credentials', ['id'], unique=False)
    op.create_index(op.f('ix_passkey_credentials_user_id'), 'passkey_credentials', ['user_id'], unique=False)
    op.add_column('users', sa.Column('phone', sa.Integer(), nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.drop_index('ix_users_email', table_name='users')
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.drop_column('users', 'email')


def downgrade() -> None:
    op.add_column('users', sa.Column('email', sa.VARCHAR(), nullable=False))
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.create_index('ix_users_email', 'users', ['email'], unique=1)
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'phone')
    op.drop_index(op.f('ix_passkey_credentials_user_id'), table_name='passkey_credentials')
    op.drop_index(op.f('ix_passkey_credentials_id'), table_name='passkey_credentials')
    op.drop_index(op.f('ix_passkey_credentials_credential_id'), table_name='passkey_credentials')
    op.drop_table('passkey_credentials')
    # ### end Alembic commands ###
