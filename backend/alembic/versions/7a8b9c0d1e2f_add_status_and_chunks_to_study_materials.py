"""add status error_message and num_chunks to study_materials

Revision ID: 7a8b9c0d1e2f
Revises: e4c57637e8d0
Create Date: 2026-10-02 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a8b9c0d1e2f'
down_revision: Union[str, Sequence[str], None] = 'e4c57637e8d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'study_materials',
        sa.Column('status', sa.String(length=20), server_default='completed', nullable=False)
    )
    op.add_column(
        'study_materials',
        sa.Column('error_message', sa.Text(), nullable=True)
    )
    op.add_column(
        'study_materials',
        sa.Column('num_chunks', sa.Integer(), server_default='0', nullable=False)
    )


def downgrade() -> None:
    op.drop_column('study_materials', 'num_chunks')
    op.drop_column('study_materials', 'error_message')
    op.drop_column('study_materials', 'status')
