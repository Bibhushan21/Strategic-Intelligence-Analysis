"""
Migration script to add user authentication to Strategic Intelligence App.
Adds User table and updates existing tables to support user relationships.
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
from data.models import User, AnalysisSession, AnalysisTemplate, AgentRating


def run_migration():
    """Run the user authentication migration."""
    print("Starting user authentication migration...")
    
    try:
        print(f"Connecting to database...")
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # 1. Create User table if it doesn't exist
            print("Creating User table...")
            Base.metadata.create_all(engine, tables=[User.__table__])
            
            # 2. Add user_id columns to existing tables if they don't exist
            print("Adding user_id columns to existing tables...")
            
            # Check and add user_id to analysis_sessions
            try:
                session.execute(text("ALTER TABLE analysis_sessions ADD COLUMN user_id INTEGER"))
                print("✓ Added user_id column to analysis_sessions")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print("✓ user_id column already exists in analysis_sessions")
                else:
                    print(f"Warning: Could not add user_id to analysis_sessions: {e}")
            
            # Check and add user_id to analysis_templates
            try:
                session.execute(text("ALTER TABLE analysis_templates ADD COLUMN user_id INTEGER"))
                print("✓ Added user_id column to analysis_templates")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print("✓ user_id column already exists in analysis_templates")
                else:
                    print(f"Warning: Could not add user_id to analysis_templates: {e}")
            
            # Update agent_ratings user_id column type from string to integer
            try:
                # First, check if the column exists and its type
                result = session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'agent_ratings' AND column_name = 'user_id'
                """))
                
                column_info = result.fetchone()
                if column_info and 'character' in column_info[1].lower():
                    print("Converting agent_ratings.user_id from string to integer...")
                    
                    # Add new integer column
                    session.execute(text("ALTER TABLE agent_ratings ADD COLUMN user_id_new INTEGER"))
                    
                    # Drop the old column
                    session.execute(text("ALTER TABLE agent_ratings DROP COLUMN user_id"))
                    
                    # Rename the new column
                    session.execute(text("ALTER TABLE agent_ratings RENAME COLUMN user_id_new TO user_id"))
                    
                    print("✓ Converted agent_ratings.user_id to integer type")
                else:
                    print("✓ agent_ratings.user_id is already integer type or doesn't exist")
                    
            except Exception as e:
                print(f"Warning: Could not update agent_ratings.user_id: {e}")
            
            # 3. Add foreign key constraints (if supported by the database)
            print("Adding foreign key constraints...")
            
            try:
                # Analysis sessions foreign key
                session.execute(text("""
                    ALTER TABLE analysis_sessions 
                    ADD CONSTRAINT fk_analysis_sessions_user_id 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                """))
                print("✓ Added foreign key constraint for analysis_sessions.user_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("✓ Foreign key constraint already exists for analysis_sessions.user_id")
                else:
                    print(f"Warning: Could not add foreign key for analysis_sessions.user_id: {e}")
            
            try:
                # Analysis templates foreign key
                session.execute(text("""
                    ALTER TABLE analysis_templates 
                    ADD CONSTRAINT fk_analysis_templates_user_id 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                """))
                print("✓ Added foreign key constraint for analysis_templates.user_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("✓ Foreign key constraint already exists for analysis_templates.user_id")
                else:
                    print(f"Warning: Could not add foreign key for analysis_templates.user_id: {e}")
            
            try:
                # Agent ratings foreign key
                session.execute(text("""
                    ALTER TABLE agent_ratings 
                    ADD CONSTRAINT fk_agent_ratings_user_id 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                """))
                print("✓ Added foreign key constraint for agent_ratings.user_id")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("✓ Foreign key constraint already exists for agent_ratings.user_id")
                else:
                    print(f"Warning: Could not add foreign key for agent_ratings.user_id: {e}")
            
            # 4. Create a default admin user if no users exist
            print("Checking for existing users...")
            
            user_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            if user_count == 0:
                print("Creating default admin user...")
                
                # Import password hashing function
                from app.core.auth import get_password_hash
                
                # Create admin user
                admin_user_query = text("""
                    INSERT INTO users (username, email, hashed_password, full_name, is_active, is_verified, created_at, login_count)
                    VALUES (:username, :email, :hashed_password, :full_name, :is_active, :is_verified, NOW(), 0)
                """)
                
                session.execute(admin_user_query, {
                    'username': 'admin',
                    'email': 'admin@strategicai.com',
                    'hashed_password': get_password_hash('admin123'),
                    'full_name': 'System Administrator',
                    'is_active': True,
                    'is_verified': True
                })
                
                print("✓ Created default admin user (username: admin, password: admin123)")
                print("⚠️  Please change the default admin password after first login!")
            else:
                print(f"✓ Found {user_count} existing users")
            
            # Commit all changes
            session.commit()
            print("\n✅ User authentication migration completed successfully!")
            
            print("\n📋 Next steps:")
            print("1. Update your .env file with a strong SECRET_KEY")
            print("2. If you created the default admin user, change the password after first login")
            print("3. Test the login functionality")
            print("4. Update any existing API calls to handle authentication")
            
        except Exception as e:
            session.rollback()
            print(f"\n❌ Migration failed: {e}")
            raise
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Could not connect to database: {e}")
        raise


if __name__ == "__main__":
    run_migration() 