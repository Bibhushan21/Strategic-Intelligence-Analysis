#!/usr/bin/env python3
"""
Quick Database Fix for Cloud Deployment
Minimal script to fix authentication and schema issues.
"""

import os
import sys
from pathlib import Path

# Add data directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'data'))

def quick_fix():
    """Quick fix for common cloud deployment issues."""
    try:
        print("🔧 Quick database fix...")
        
        from data.database_config import get_db_connection
        from app.core.auth import get_password_hash
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Fix login_count NULL values
            cursor.execute("UPDATE users SET login_count = 0 WHERE login_count IS NULL")
            print("✅ Fixed login_count NULL values")
            
            # 2. Ensure admin user exists with proper fields
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            
            if not admin:
                hashed_password = get_password_hash("admin123")
                cursor.execute("""
                    INSERT INTO users (username, email, hashed_password, full_name, is_active, is_verified, is_admin, login_count, created_at)
                    VALUES ('admin', 'admin@challenges.one', %s, 'System Administrator', true, true, true, 0, NOW())
                """, (hashed_password,))
                print("✅ Created admin user")
            else:
                cursor.execute("""
                    UPDATE users 
                    SET email = 'admin@challenges.one', is_admin = true, is_active = true, is_verified = true, login_count = COALESCE(login_count, 0)
                    WHERE username = 'admin'
                """)
                print("✅ Updated admin user")
            
            conn.commit()
            print("✅ Database fix completed!")
            return True
            
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_fix()
    if not success:
        sys.exit(1) 