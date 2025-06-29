#!/usr/bin/env python3
"""
Emergency Schema Fix for Cloud Deployment
Fixes the missing user_id column in analysis_sessions table.
"""

import os
import sys
import logging
from pathlib import Path

# Add data directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'data'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_missing_user_id():
    """Fix the missing user_id column in analysis_sessions."""
    try:
        print("🚨 EMERGENCY SCHEMA FIX")
        print("=" * 40)
        
        from data.database_config import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user_id column exists in analysis_sessions
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'analysis_sessions' AND column_name = 'user_id'
            """)
            exists = cursor.fetchone()
            
            if not exists:
                print("❌ user_id column missing in analysis_sessions")
                print("🔧 Adding user_id column...")
                
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN user_id INTEGER")
                
                # Set existing records to admin user (id=1)
                cursor.execute("UPDATE analysis_sessions SET user_id = 1 WHERE user_id IS NULL")
                
                conn.commit()
                print("✅ Fixed: Added user_id column to analysis_sessions")
            else:
                print("✅ user_id column already exists in analysis_sessions")
                
            # Check if user_id column exists in agent_results
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_results' AND column_name = 'user_id'
            """)
            exists = cursor.fetchone()
            
            if not exists:
                print("🔧 Adding user_id column to agent_results...")
                cursor.execute("ALTER TABLE agent_results ADD COLUMN user_id INTEGER")
                cursor.execute("UPDATE agent_results SET user_id = 1 WHERE user_id IS NULL")
                conn.commit()
                print("✅ Fixed: Added user_id column to agent_results")
            else:
                print("✅ user_id column already exists in agent_results")
            
            print("\n🎉 SCHEMA FIX COMPLETED!")
            print("The application should now work properly.")
            return True
            
    except Exception as e:
        logger.error(f"❌ Schema fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_missing_user_id()
    if not success:
        sys.exit(1) 