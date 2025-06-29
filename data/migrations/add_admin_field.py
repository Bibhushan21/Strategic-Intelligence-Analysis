#!/usr/bin/env python3
"""
Migration: Add is_admin field to User table
This migration adds an is_admin boolean field to the users table
and sets the admin user as admin.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'data'))

try:
    from database_config import get_db_connection, test_connection, engine
    from models import Base, User
    from sqlalchemy import text
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def add_admin_field():
        """Add is_admin field to users table and set admin user as admin"""
        
        try:
            # Test database connection
            if not test_connection():
                logger.error("Cannot connect to database")
                return False
            
            logger.info("Starting migration: Add is_admin field to users table")
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if is_admin column already exists
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'is_admin'
                """)
                
                if cursor.fetchone():
                    logger.info("is_admin column already exists")
                    return True
                
                # Add is_admin column to users table
                logger.info("Adding is_admin column to users table...")
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
                """)
                
                # Set admin user as admin
                logger.info("Setting admin user as admin...")
                cursor.execute("""
                    UPDATE users 
                    SET is_admin = TRUE 
                    WHERE username = 'admin' OR email = 'admin@strategicai.com'
                """)
                
                rows_updated = cursor.rowcount
                logger.info(f"Updated {rows_updated} admin user(s)")
                
                # Commit the changes
                conn.commit()
                logger.info("Migration completed successfully!")
                
                # Verify the changes
                cursor.execute("""
                    SELECT username, email, is_admin 
                    FROM users 
                    WHERE is_admin = TRUE
                """)
                
                admin_users = cursor.fetchall()
                if admin_users:
                    logger.info("Admin users found:")
                    for user in admin_users:
                        logger.info(f"  - {user[0]} ({user[1]}) - Admin: {user[2]}")
                else:
                    logger.warning("No admin users found!")
                
                return True
                
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False

    def rollback_admin_field():
        """Remove is_admin field from users table"""
        
        try:
            logger.info("Rolling back migration: Remove is_admin field from users table")
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Remove is_admin column
                cursor.execute("""
                    ALTER TABLE users 
                    DROP COLUMN IF EXISTS is_admin
                """)
                
                conn.commit()
                logger.info("Rollback completed successfully!")
                return True
                
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False

    if __name__ == "__main__":
        import argparse
        
        parser = argparse.ArgumentParser(description='Add is_admin field to users table')
        parser.add_argument('--rollback', action='store_true', 
                          help='Rollback the migration (remove is_admin field)')
        
        args = parser.parse_args()
        
        if args.rollback:
            success = rollback_admin_field()
        else:
            success = add_admin_field()
        
        if success:
            logger.info("Operation completed successfully!")
            sys.exit(0)
        else:
            logger.error("Operation failed!")
            sys.exit(1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 