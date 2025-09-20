"""Add wizard sessions table

Revision ID: 001
Revises: 
Create Date: 2024-01-19 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create wizard_sessions table
    op.create_table('wizard_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('state', sa.String(50), nullable=False),
        sa.Column('vehicle_data', sa.Text(), nullable=True),
        sa.Column('part_data', sa.Text(), nullable=True),
        sa.Column('contact_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for user_id lookups
    op.create_index('idx_wizard_sessions_user_id', 'wizard_sessions', ['user_id'])


def downgrade():
    op.drop_index('idx_wizard_sessions_user_id', table_name='wizard_sessions')
    op.drop_table('wizard_sessions')
