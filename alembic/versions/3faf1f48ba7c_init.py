"""init

Revision ID: 3faf1f48ba7c
Revises: 
Create Date: 2023-12-06 10:32:48.941716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3faf1f48ba7c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('msisdn', sa.String(length=15), nullable=False),
    sa.Column('hashed_msisdn', sa.Text(), nullable=False),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('msisdn', 'hashed_msisdn', name='unique_profile')
    )
    op.create_index(op.f('ix_profile_hashed_msisdn'), 'profile', ['hashed_msisdn'], unique=False)
    op.create_index(op.f('ix_profile_id'), 'profile', ['id'], unique=False)
    op.create_index(op.f('ix_profile_msisdn'), 'profile', ['msisdn'], unique=False)
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'INTERNAL_ERROR', 'ACCEPTED_BY_BTOBET', 'REJECTED_BY_BTOBET', 'UNKNOWN_BTOBET_STATUS', name='status'), nullable=False),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('org_account_balance', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('transaction_type', sa.String(length=30), nullable=False),
    sa.Column('mpesa_ref_number', sa.String(length=30), nullable=False),
    sa.Column('msisdn', sa.String(length=15), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_id'), 'payment', ['id'], unique=False)
    op.create_index(op.f('ix_payment_mpesa_ref_number'), 'payment', ['mpesa_ref_number'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payment_mpesa_ref_number'), table_name='payment')
    op.drop_index(op.f('ix_payment_id'), table_name='payment')
    op.drop_table('payment')
    op.drop_index(op.f('ix_profile_msisdn'), table_name='profile')
    op.drop_index(op.f('ix_profile_id'), table_name='profile')
    op.drop_index(op.f('ix_profile_hashed_msisdn'), table_name='profile')
    op.drop_table('profile')
    # ### end Alembic commands ###
