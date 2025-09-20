"""Add enhanced user management

Revision ID: 4230884aa0a8
Revises: 34e2c2a073ed
Create Date: 2025-09-20 02:43:08.327199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4230884aa0a8'
down_revision = '34e2c2a073ed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('parts', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_parts_category_id', 'part_categories', ['category_id'], ['id'])
    
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Add new columns with default values for existing records
        batch_op.add_column(sa.Column('salt', sa.String(length=32), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('first_name', sa.String(length=50), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('last_name', sa.String(length=50), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('login_attempts', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('locked_until', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('password_changed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.add_column(sa.Column('avatar_url', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'))
        batch_op.add_column(sa.Column('language', sa.String(length=10), nullable=False, server_default='en'))
        batch_op.add_column(sa.Column('preferences', sa.JSON(), nullable=True))
        
        # Modify existing columns
        batch_op.alter_column('username',
                   existing_type=sa.VARCHAR(length=100),
                   type_=sa.String(length=50),
                   existing_nullable=False)
        batch_op.alter_column('email',
                   existing_type=sa.VARCHAR(length=255),
                   type_=sa.String(length=100),
                   existing_nullable=True,
                   nullable=False)
        
        # Create index
        batch_op.create_index('ix_users_email', ['email'], unique=True)


def downgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_email')
        batch_op.alter_column('email',
                   existing_type=sa.String(length=100),
                   type_=sa.VARCHAR(length=255),
                   nullable=True)
        batch_op.alter_column('username',
                   existing_type=sa.String(length=50),
                   type_=sa.VARCHAR(length=100),
                   existing_nullable=False)
        batch_op.drop_column('preferences')
        batch_op.drop_column('language')
        batch_op.drop_column('timezone')
        batch_op.drop_column('avatar_url')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('password_changed_at')
        batch_op.drop_column('locked_until')
        batch_op.drop_column('login_attempts')
        batch_op.drop_column('is_verified')
        batch_op.drop_column('phone')
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')
        batch_op.drop_column('salt')
    
    with op.batch_alter_table('parts', schema=None) as batch_op:
        batch_op.drop_constraint('fk_parts_category_id', type_='foreignkey')
