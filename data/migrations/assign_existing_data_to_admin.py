"""
Script to assign existing data to the admin user.
This ensures that existing analysis sessions, templates, and ratings
are not lost and can be accessed by the admin user.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from data.database_config import Base, DATABASE_URL


def assign_existing_data_to_admin():
    """Assign all existing data to the admin user."""
    print("Assigning existing data to admin user...")
    
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Get the admin user ID
            admin_user = session.execute(text("""
                SELECT id FROM users WHERE username = 'admin' LIMIT 1
            """)).fetchone()
            
            if not admin_user:
                print("❌ Admin user not found. Please run the authentication migration first.")
                return
            
            admin_id = admin_user[0]
            print(f"✓ Found admin user with ID: {admin_id}")
            
            # Update analysis_sessions without user_id
            result = session.execute(text("""
                UPDATE analysis_sessions 
                SET user_id = :admin_id 
                WHERE user_id IS NULL
            """), {"admin_id": admin_id})
            
            sessions_updated = result.rowcount
            print(f"✓ Assigned {sessions_updated} analysis sessions to admin user")
            
            # Update analysis_templates without user_id (keep system templates as NULL)
            result = session.execute(text("""
                UPDATE analysis_templates 
                SET user_id = :admin_id 
                WHERE user_id IS NULL AND created_by != 'system'
            """), {"admin_id": admin_id})
            
            templates_updated = result.rowcount
            print(f"✓ Assigned {templates_updated} non-system templates to admin user")
            
            # Update agent_ratings without user_id
            result = session.execute(text("""
                UPDATE agent_ratings 
                SET user_id = :admin_id 
                WHERE user_id IS NULL
            """), {"admin_id": admin_id})
            
            ratings_updated = result.rowcount
            print(f"✓ Assigned {ratings_updated} agent ratings to admin user")
            
            # Commit all changes
            session.commit()
            
            print(f"\n✅ Successfully assigned existing data to admin user!")
            print(f"📊 Summary:")
            print(f"   - Analysis Sessions: {sessions_updated}")
            print(f"   - Templates: {templates_updated}")
            print(f"   - Ratings: {ratings_updated}")
            
            # Show counts of data now assigned to admin
            admin_sessions = session.execute(text("""
                SELECT COUNT(*) FROM analysis_sessions WHERE user_id = :admin_id
            """), {"admin_id": admin_id}).scalar()
            
            admin_templates = session.execute(text("""
                SELECT COUNT(*) FROM analysis_templates WHERE user_id = :admin_id
            """), {"admin_id": admin_id}).scalar()
            
            admin_ratings = session.execute(text("""
                SELECT COUNT(*) FROM agent_ratings WHERE user_id = :admin_id
            """), {"admin_id": admin_id}).scalar()
            
            print(f"\n📈 Admin user now has access to:")
            print(f"   - {admin_sessions} analysis sessions")
            print(f"   - {admin_templates} templates")
            print(f"   - {admin_ratings} ratings")
            
        except Exception as e:
            session.rollback()
            print(f"\n❌ Failed to assign data: {e}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Could not connect to database: {e}")
        raise


if __name__ == "__main__":
    assign_existing_data_to_admin() 