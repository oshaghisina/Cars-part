#!/usr/bin/env python3
"""
Migration script to add SMS-related columns to the users table.
"""

import sqlite3
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings


def migrate_users_table():
    """Add SMS-related columns to the users table."""
    print("🔄 Migrating users table to add SMS columns...")
    
    # Connect to the database
    db_path = settings.database_url.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns
        new_columns = [
            ("sms_notifications", "BOOLEAN DEFAULT 1"),
            ("sms_marketing", "BOOLEAN DEFAULT 1"), 
            ("sms_delivery", "BOOLEAN DEFAULT 1"),
            ("phone_verified", "BOOLEAN DEFAULT 0")
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in columns:
                print(f"  ➕ Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
            else:
                print(f"  ✅ Column already exists: {column_name}")
        
        # Commit changes
        conn.commit()
        print("✅ Users table migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_users_table()
