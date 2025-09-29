"""add_version_tracking_to_models

Revision ID: 2f34dc5a1e0e
Revises: 4230884aa0a8
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '2f34dc5a1e0e'
down_revision = '4230884aa0a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add version tracking columns and tables."""
    # Get existing tables and columns for idempotent migration
    from sqlalchemy import inspect
    inspector = inspect(op.get_bind())
    existing_tables = inspector.get_table_names()
    
    # Create part_versions table only if it doesn't exist
    if 'part_versions' not in existing_tables:
        op.create_table('part_versions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('part_id', sa.Integer(), nullable=False),
            sa.Column('version', sa.Integer(), nullable=False),
            sa.Column('changes', sa.JSON(), nullable=False),
            sa.Column('changed_by', sa.String(length=100), nullable=True),
            sa.Column('change_reason', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_part_versions_id'), 'part_versions', ['id'], unique=False)
    
    # Create stock_versions table only if it doesn't exist
    if 'stock_versions' not in existing_tables:
        op.create_table('stock_versions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('stock_id', sa.Integer(), nullable=False),
            sa.Column('version', sa.Integer(), nullable=False),
            sa.Column('changes', sa.JSON(), nullable=False),
            sa.Column('changed_by', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['stock_id'], ['stock_levels.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_stock_versions_id'), 'stock_versions', ['id'], unique=False)
    
    # Add version tracking columns to parts table only if they don't exist
    if 'parts' in existing_tables:
        parts_columns = [col['name'] for col in inspector.get_columns('parts')]
        if 'current_version' not in parts_columns:
            op.add_column('parts', sa.Column('current_version', sa.Integer(), nullable=False, server_default='1'))
        if 'last_updated_by' not in parts_columns:
            op.add_column('parts', sa.Column('last_updated_by', sa.String(length=100), nullable=True))
    
    # Add version tracking columns to stock_levels table only if they don't exist
    if 'stock_levels' in existing_tables:
        stock_columns = [col['name'] for col in inspector.get_columns('stock_levels')]
        if 'version' not in stock_columns:
            op.add_column('stock_levels', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
        if 'updated_by' not in stock_columns:
            op.add_column('stock_levels', sa.Column('updated_by', sa.String(length=100), nullable=True))
        if 'lock_timestamp' not in stock_columns:
            op.add_column('stock_levels', sa.Column('lock_timestamp', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove version tracking columns and tables."""
    # Remove version tracking columns from stock_levels
    op.drop_column('stock_levels', 'lock_timestamp')
    op.drop_column('stock_levels', 'updated_by')
    op.drop_column('stock_levels', 'version')
    
    # Remove version tracking columns from parts
    op.drop_column('parts', 'last_updated_by')
    op.drop_column('parts', 'current_version')
    
    # Drop version tracking tables
    op.drop_index(op.f('ix_stock_versions_id'), table_name='stock_versions')
    op.drop_table('stock_versions')
    op.drop_index(op.f('ix_part_versions_id'), table_name='part_versions')
    op.drop_table('part_versions')