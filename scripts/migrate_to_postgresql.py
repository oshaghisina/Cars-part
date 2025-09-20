#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL
This script migrates data from SQLite to PostgreSQL for production deployment.
"""

import os
import sys
import sqlite3
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.models import Base, Part, Price, Synonym, Lead, Order, OrderItem, Setting, User
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sqlite_data(sqlite_path):
    """Extract data from SQLite database."""
    logger.info(f"Extracting data from SQLite: {sqlite_path}")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # Extract all tables
    tables_data = {}
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        if table == 'alembic_version':
            continue
            
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        tables_data[table] = [dict(row) for row in rows]
        logger.info(f"Extracted {len(rows)} rows from {table}")
    
    sqlite_conn.close()
    return tables_data

def create_postgresql_tables(postgresql_url):
    """Create tables in PostgreSQL database."""
    logger.info(f"Creating tables in PostgreSQL: {postgresql_url}")
    
    # Create engine and tables
    engine = create_engine(postgresql_url)
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL tables created successfully")

def insert_data_to_postgresql(postgresql_url, tables_data):
    """Insert data into PostgreSQL tables."""
    logger.info("Inserting data into PostgreSQL...")
    
    engine = create_engine(postgresql_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Insert data in order (respecting foreign key constraints)
        insert_order = ['users', 'settings', 'parts', 'prices', 'synonyms', 'leads', 'orders', 'order_items']
        
        for table_name in insert_order:
            if table_name in tables_data and tables_data[table_name]:
                table_class = {
                    'users': User,
                    'settings': Setting,
                    'parts': Part,
                    'prices': Price,
                    'synonyms': Synonym,
                    'leads': Lead,
                    'orders': Order,
                    'order_items': OrderItem
                }.get(table_name)
                
                if table_class:
                    for row_data in tables_data[table_name]:
                        try:
                            # Create instance and add to session
                            instance = table_class(**row_data)
                            db.add(instance)
                        except Exception as e:
                            logger.warning(f"Error inserting row in {table_name}: {e}")
                            continue
                    
                    db.commit()
                    logger.info(f"Inserted {len(tables_data[table_name])} rows into {table_name}")
        
        logger.info("Data migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during data insertion: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_migration(postgresql_url):
    """Verify that migration was successful."""
    logger.info("Verifying migration...")
    
    engine = create_engine(postgresql_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Count records in each table
        tables = [User, Setting, Part, Price, Synonym, Lead, Order, OrderItem]
        total_records = 0
        
        for table in tables:
            count = db.query(table).count()
            logger.info(f"{table.__name__}: {count} records")
            total_records += count
        
        logger.info(f"Total records migrated: {total_records}")
        
        # Test a sample query
        parts_count = db.query(Part).count()
        if parts_count > 0:
            sample_part = db.query(Part).first()
            logger.info(f"Sample part: {sample_part.part_name} - {sample_part.vehicle_model}")
        
        logger.info("✅ Migration verification successful!")
        
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        raise
    finally:
        db.close()

def main():
    """Main migration function."""
    logger.info("🚀 Starting SQLite to PostgreSQL migration")
    
    # Configuration
    sqlite_path = "data/app.db"
    postgresql_url = "postgresql://admin:secure_password@localhost:5432/china_car_parts"
    
    # Check if SQLite database exists
    if not os.path.exists(sqlite_path):
        logger.error(f"SQLite database not found: {sqlite_path}")
        sys.exit(1)
    
    try:
        # Step 1: Extract data from SQLite
        tables_data = get_sqlite_data(sqlite_path)
        
        # Step 2: Create PostgreSQL tables
        create_postgresql_tables(postgresql_url)
        
        # Step 3: Insert data into PostgreSQL
        insert_data_to_postgresql(postgresql_url, tables_data)
        
        # Step 4: Verify migration
        verify_migration(postgresql_url)
        
        logger.info("🎉 Migration completed successfully!")
        logger.info("You can now update your .env file to use PostgreSQL:")
        logger.info(f"DATABASE_URL={postgresql_url}")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
