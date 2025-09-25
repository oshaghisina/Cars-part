#!/usr/bin/env python3
"""
Script to create Telegram SSO database tables.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.db.database import engine, Base
from app.models.telegram_models import (
    TelegramUser,
    TelegramLinkToken,
    TelegramBotSession,
    TelegramDeepLink,
)
from app.db.models import User


def create_telegram_tables():
    """Create Telegram SSO database tables."""
    print("🔄 Creating Telegram SSO database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Telegram SSO tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        telegram_tables = [
            'telegram_users',
            'telegram_link_tokens',
            'telegram_bot_sessions',
            'telegram_deep_links'
        ]
        
        for table in telegram_tables:
            if table in tables:
                print(f"  ✅ {table} table created")
            else:
                print(f"  ❌ {table} table not found")
        
        print("🎉 Telegram SSO database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating Telegram tables: {e}")
        raise


if __name__ == "__main__":
    create_telegram_tables()
