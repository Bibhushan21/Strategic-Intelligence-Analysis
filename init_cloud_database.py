#!/usr/bin/env python3
"""
Comprehensive Cloud Database Setup for challenges.one
This script handles complete database initialization including schema updates, 
user setup, templates, and verification for both new and existing deployments.
"""

import os
import sys
import logging
from pathlib import Path

# Add data directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'data'))

# Setup logging with minimal output for cloud deployment
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_cloud_database():
    """
    Comprehensive cloud database initialization.
    Handles both new deployments and existing database updates.
    """
    try:
        print("🚀 Starting database setup...")
        
        # Test database connection
        if not test_database_connection():
            print("❌ Database connection failed!")
            return False
        
        # Create all tables using SQLAlchemy
        create_database_tables()
        
        # Update database schema (add missing columns)
        if not update_database_schema():
            print("❌ Schema update failed!")
            return False
        
        # Setup admin user
        if not setup_admin_user_sql():
            print("❌ Admin user setup failed!")
            return False
        
        # Create templates
        if not create_templates_sql():
            print("❌ Template creation failed!")
            return False
        
        # Initialize rating summaries
        initialize_ratings_sql()
        
        print("✅ Database setup completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Comprehensive setup failed: {str(e)}")
        return False

def test_database_connection():
    """Test database connection."""
    try:
        from data.database_config import test_connection
        return test_connection()
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def update_database_schema():
    """Update database schema with missing columns for existing databases."""
    try:
        from data.database_config import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            logger.info("🔧 Checking and updating database schema...")
            
            # Update analysis_templates table
            update_analysis_templates_schema(cursor, conn)
            
            # Update users table
            update_users_schema(cursor, conn)
            
            # Update other tables
            update_other_tables_schema(cursor, conn)
            
            logger.info("✅ Schema update completed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Schema update failed: {str(e)}")
        return False

def update_analysis_templates_schema(cursor, conn):
    """Add missing columns to analysis_templates table."""
    try:
        logger.info("📋 Updating analysis_templates table schema...")
        
        columns_to_add = [
            ("strategic_question_template", "TEXT"),
            ("default_time_frame", "VARCHAR(50)"),
            ("default_region", "VARCHAR(100)"),
            ("default_instructions", "TEXT"),
            ("tags", "JSON"),
            ("is_public", "BOOLEAN DEFAULT true"),
            ("created_by", "VARCHAR(100) DEFAULT 'system'"),
            ("usage_count", "INTEGER DEFAULT 0"),
            ("is_active", "BOOLEAN DEFAULT true"),
            ("updated_at", "TIMESTAMP")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                # Each column addition in its own transaction
                sql = f"ALTER TABLE analysis_templates ADD COLUMN {column_name} {column_def}"
                cursor.execute(sql)
                conn.commit()  # Commit immediately after each successful addition
                logger.info(f"   ✅ Added column: {column_name}")
            except Exception as e:
                conn.rollback()  # Rollback the failed operation
                if "already exists" in str(e):
                    logger.info(f"   ⏭️  Column {column_name} already exists")
                else:
                    logger.warning(f"   ⚠️  Could not add {column_name}: {e}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update analysis_templates schema: {e}")

def update_users_schema(cursor, conn):
    """Add missing columns to users table."""
    try:
        logger.info("👤 Updating users table schema...")
        
        columns_to_add = [
            ("full_name", "VARCHAR(100)"),
            ("is_active", "BOOLEAN DEFAULT true"),
            ("is_verified", "BOOLEAN DEFAULT false"),
            ("is_admin", "BOOLEAN DEFAULT false"),
            ("last_login", "TIMESTAMP"),
            ("login_count", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                # Each column addition in its own transaction
                sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                cursor.execute(sql)
                conn.commit()  # Commit immediately after each successful addition
                logger.info(f"   ✅ Added column: {column_name}")
            except Exception as e:
                conn.rollback()  # Rollback the failed operation
                if "already exists" in str(e):
                    logger.info(f"   ⏭️  Column {column_name} already exists")
                else:
                    logger.warning(f"   ⚠️  Could not add {column_name}: {e}")
        
    except Exception as e:
        logger.error(f"❌ Failed to update users schema: {e}")

def update_other_tables_schema(cursor, conn):
    """Add missing columns to other tables."""
    try:
        logger.info("🔧 Updating other tables schema...")
        
        # Add user_id to analysis_sessions - this is critical for user authentication
        try:
            # First check if column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'analysis_sessions' AND column_name = 'user_id'
            """)
            result = cursor.fetchone()
            
            if not result:
                logger.info("   🔄 Adding user_id column to analysis_sessions...")
                cursor.execute("ALTER TABLE analysis_sessions ADD COLUMN user_id INTEGER")
                conn.commit()  # Commit the column addition
                logger.info("   ✅ Added user_id to analysis_sessions")
                
                # Add foreign key constraint if possible
                try:
                    cursor.execute("""
                        ALTER TABLE analysis_sessions 
                        ADD CONSTRAINT fk_analysis_sessions_user_id 
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    """)
                    conn.commit()  # Commit the constraint addition
                    logger.info("   ✅ Added foreign key constraint for user_id")
                except Exception as fk_e:
                    conn.rollback()  # Rollback only the constraint, not the column
                    logger.warning(f"   ⚠️  Could not add foreign key constraint: {fk_e}")
                    
            else:
                logger.info("   ⏭️  user_id already exists in analysis_sessions")
                
        except Exception as e:
            logger.error(f"   ❌ CRITICAL: Could not add user_id to analysis_sessions: {e}")
            # This is critical - re-raise the exception
            raise
        
        # Add user_id to agent_results if missing
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_results' AND column_name = 'user_id'
            """)
            result = cursor.fetchone()
            
            if not result:
                cursor.execute("ALTER TABLE agent_results ADD COLUMN user_id INTEGER")
                conn.commit()  # Commit the column addition
                logger.info("   ✅ Added user_id to agent_results")
            else:
                logger.info("   ⏭️  user_id already exists in agent_results")
                
        except Exception as e:
            logger.warning(f"   ⚠️  Could not add user_id to agent_results: {e}")
        
        # Convert agent_ratings.user_id from string to integer if needed
        try:
            cursor.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'agent_ratings' AND column_name = 'user_id'
            """)
            result = cursor.fetchone()
            
            if result and 'character' in result[0].lower():
                logger.info("   🔄 Converting agent_ratings.user_id from string to integer...")
                cursor.execute("ALTER TABLE agent_ratings ADD COLUMN user_id_new INTEGER")
                cursor.execute("""
                    UPDATE agent_ratings 
                    SET user_id_new = CASE 
                        WHEN user_id ~ '^[0-9]+$' THEN user_id::INTEGER 
                        ELSE 1 
                    END
                """)
                cursor.execute("ALTER TABLE agent_ratings DROP COLUMN user_id")
                cursor.execute("ALTER TABLE agent_ratings RENAME COLUMN user_id_new TO user_id")
                conn.commit()  # Commit all the conversion operations together
                logger.info("   ✅ Converted agent_ratings.user_id to integer")
            else:
                logger.info("   ⏭️  agent_ratings.user_id already correct type")
                
        except Exception as e:
            logger.warning(f"   ⚠️  Could not update agent_ratings.user_id: {e}")
        
        logger.info("✅ Other tables schema update completed!")
        
    except Exception as e:
        logger.error(f"❌ Failed to update other tables schema: {e}")
        conn.rollback()
        raise

def create_database_tables():
    """Create all database tables using SQLAlchemy."""
    try:
        from data.database_config import engine, Base
        from data.models import (
            User, AnalysisSession, AgentResult, AnalysisTemplate,
            SystemLog, AgentPerformance, AgentRating, AgentRatingSummary
        )
        
        # Create all tables (safe - won't overwrite existing)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All database tables created/verified!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Table creation failed: {e}")
        return False

def setup_admin_user_sql():
    """Setup admin user using direct SQL for reliability."""
    try:
        from app.core.auth import get_password_hash
        from data.database_config import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if admin exists
            cursor.execute("SELECT id, username, email, is_admin FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            
            if admin:
                logger.info("👤 Updating existing admin user...")
                cursor.execute("""
                    UPDATE users 
                    SET email = 'admin@challenges.one', 
                        is_admin = true, 
                        is_active = true, 
                        is_verified = true 
                    WHERE username = 'admin'
                """)
                logger.info("✅ Admin user updated!")
            else:
                logger.info("👤 Creating new admin user...")
                hashed_password = get_password_hash("admin123")
                cursor.execute("""
                    INSERT INTO users (username, email, hashed_password, full_name, is_active, is_verified, is_admin, created_at)
                    VALUES ('admin', 'admin@challenges.one', %s, 'System Administrator', true, true, true, NOW())
                """, (hashed_password,))
                logger.info("✅ Admin user created!")
                logger.info("   🔑 Username: admin")
                logger.info("   📧 Email: admin@challenges.one")
                logger.info("   🔐 Password: admin123")
                logger.info("   ⚠️  IMPORTANT: Change the default password after first login!")
            
            conn.commit()
            return True
            
    except Exception as e:
        logger.error(f"❌ Admin setup failed: {e}")
        return False

def create_templates_sql():
    """Create analysis templates using direct SQL for reliability."""
    try:
        from data.database_config import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if templates exist
            cursor.execute("SELECT COUNT(*) FROM analysis_templates")
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.info(f"📋 Found {count} existing templates, skipping creation")
                return True
            
            logger.info("📝 Creating analysis templates...")
            
            templates = [
                {
                    'name': 'Market Entry Strategy',
                    'description': 'Comprehensive analysis for entering new markets',
                    'category': 'Business Strategy',
                    'strategic_question_template': 'What are the key considerations and strategic approach for entering new markets?',
                    'default_time_frame': 'medium_term',
                    'default_region': 'global',
                    'default_instructions': 'Focus on competitive landscape, regulatory environment, and market dynamics',
                    'tags': '["market-entry", "strategy", "business-development"]',
                    'is_public': True,
                    'created_by': 'system'
                },
                {
                    'name': 'Technology Impact Analysis',
                    'description': 'Analysis of emerging technology impacts',
                    'category': 'Technology',
                    'strategic_question_template': 'How will emerging technologies impact our industry and business?',
                    'default_time_frame': 'long_term',
                    'default_region': 'global',
                    'default_instructions': 'Focus on technological trends and competitive implications',
                    'tags': '["technology", "disruption", "innovation"]',
                    'is_public': True,
                    'created_by': 'system'
                },
                {
                    'name': 'Competitive Intelligence',
                    'description': 'Comprehensive competitor analysis',
                    'category': 'Competitive Analysis',
                    'strategic_question_template': 'What are the competitive dynamics and positioning in our market?',
                    'default_time_frame': 'short_term',
                    'default_region': 'global',
                    'default_instructions': 'Analyze competitor strengths, weaknesses, and strategic moves',
                    'tags': '["competition", "market-analysis", "strategy"]',
                    'is_public': True,
                    'created_by': 'system'
                },
                {
                    'name': 'EV Industry Analysis',
                    'description': 'Electric Vehicle industry market analysis',
                    'category': 'Industry Analysis',
                    'strategic_question_template': 'What are the key market opportunities and strategic considerations for EV Industry?',
                    'default_time_frame': 'long_term',
                    'default_region': 'asia',
                    'default_instructions': 'Focus on technological advances, infrastructure development, and market penetration strategies',
                    'tags': '["electric-vehicles", "automotive", "sustainability"]',
                    'is_public': True,
                    'created_by': 'system'
                },
                {
                    'name': 'Regulatory Impact Assessment',
                    'description': 'Analysis of regulatory changes and business implications',
                    'category': 'Regulatory',
                    'strategic_question_template': 'How will upcoming regulatory changes affect our business operations?',
                    'default_time_frame': 'medium_term',
                    'default_region': 'regional',
                    'default_instructions': 'Focus on compliance requirements, business impact, and adaptive strategies',
                    'tags': '["regulation", "compliance", "risk-management"]',
                    'is_public': True,
                    'created_by': 'system'
                }
            ]
            
            for template in templates:
                cursor.execute("""
                    INSERT INTO analysis_templates 
                    (name, description, category, strategic_question_template, default_time_frame, default_region, 
                     default_instructions, tags, is_public, created_by, usage_count, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NOW())
                """, (
                    template['name'],
                    template['description'], 
                    template['category'],
                    template['strategic_question_template'],
                    template['default_time_frame'],
                    template['default_region'],
                    template['default_instructions'],
                    template['tags'],
                    template['is_public'],
                    template['created_by']
                ))
            
            conn.commit()
            logger.info(f"✅ Created {len(templates)} analysis templates!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Template creation failed: {e}")
        return False

def initialize_ratings_sql():
    """Initialize rating summaries using direct SQL."""
    try:
        from data.database_config import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            agents = [
                'Problem Explorer', 'Best Practices', 'Horizon Scanning',
                'Scenario Planning', 'Research Synthesis', 'Strategic Action', 
                'High Impact', 'Backcasting'
            ]
            
            created_count = 0
            for agent_name in agents:
                # Check if summary exists
                cursor.execute("SELECT id FROM agent_rating_summaries WHERE agent_name = %s", (agent_name,))
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute("""
                        INSERT INTO agent_rating_summaries 
                        (agent_name, total_ratings, average_rating, five_star_count, four_star_count, 
                         three_star_count, two_star_count, one_star_count, total_reviews, 
                         recommendation_percentage, last_updated)
                        VALUES (%s, 0, 0.0, 0, 0, 0, 0, 0, 0, 0.0, NOW())
                    """, (agent_name,))
                    created_count += 1
            
            conn.commit()
            
            if created_count > 0:
                logger.info(f"✅ Created {created_count} rating summaries!")
            else:
                logger.info("✅ All rating summaries already exist!")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Rating initialization failed: {e}")
        return False

def verify_complete_setup():
    """Comprehensive verification of the complete setup."""
    try:
        from data.database_config import get_db_connection
        
        logger.info("🔍 Verifying complete database setup...")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Count records in each table
            cursor.execute("SELECT COUNT(*) FROM users")
            users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_sessions")
            sessions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_templates")
            templates = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM agent_rating_summaries")
            ratings = cursor.fetchone()[0]
            
            # Get admin info
            cursor.execute("SELECT username, email, is_admin, is_active FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            
            # Check schema completeness
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'analysis_templates'
                ORDER BY column_name
            """)
            template_columns = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY column_name
            """)
            user_columns = [row[0] for row in cursor.fetchall()]
            
            print("\n" + "=" * 60)
            print("📊 COMPREHENSIVE SETUP VERIFICATION")
            print("=" * 60)
            print(f"👥 Users: {users}")
            print(f"📊 Analysis Sessions: {sessions}")
            print(f"📋 Templates: {templates}")
            print(f"⭐ Rating Summaries: {ratings}")
            
            if admin:
                print(f"🔑 Admin User: {admin[0]} ({admin[1]})")
                print(f"👑 Is Admin: {'✅' if admin[2] else '❌'}")
                print(f"🔓 Is Active: {'✅' if admin[3] else '❌'}")
            else:
                print("🔑 Admin User: ❌ NOT FOUND")
            
            print(f"\n📋 analysis_templates columns: {len(template_columns)}")
            print(f"👤 users columns: {len(user_columns)}")
            
            # Check for required columns
            required_template_cols = ['strategic_question', 'default_time_frame', 'tags', 'is_public']
            required_user_cols = ['is_admin', 'is_active', 'full_name']
            
            missing_template_cols = [col for col in required_template_cols if col not in template_columns]
            missing_user_cols = [col for col in required_user_cols if col not in user_columns]
            
            if missing_template_cols:
                print(f"⚠️  Missing template columns: {missing_template_cols}")
            if missing_user_cols:
                print(f"⚠️  Missing user columns: {missing_user_cols}")
            
            print("=" * 60)
            
            # Overall health check
            all_good = (
                users >= 1 and 
                templates >= 3 and 
                ratings >= 8 and 
                admin and admin[2] and admin[3] and  # admin exists, is_admin, is_active
                not missing_template_cols and 
                not missing_user_cols
            )
            
            if all_good:
                print("🎉 DATABASE SETUP: ✅ PERFECT!")
                print("🚀 Your challenges.one platform is ready for production!")
            else:
                print("⚠️  DATABASE SETUP: Some issues detected")
                print("📋 Review the verification details above")
            
            print("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")

def fix_schema_issues():
    """
    Standalone function to fix common schema issues without full initialization.
    Useful for fixing deployed applications with schema problems.
    """
    print("=" * 50)
    print("🔧 SCHEMA FIX MODE")
    print("=" * 50)
    
    try:
        # Test connection
        if not test_database_connection():
            return False
            
        # Fix schema issues
        logger.info("🔧 Fixing database schema issues...")
        if not update_database_schema():
            logger.error("❌ Schema fix failed!")
            return False
            
        # Verify the fix
        verify_critical_columns()
        
        print("\n✅ SCHEMA FIX COMPLETED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema fix failed: {e}")
        return False

def verify_critical_columns():
    """Verify that critical columns exist."""
    try:
        from data.database_config import get_db_connection
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check critical columns
            critical_checks = [
                ("analysis_sessions", "user_id"),
                ("agent_results", "user_id"), 
                ("users", "is_admin"),
                ("users", "is_active"),
                ("analysis_templates", "is_public")
            ]
            
            print("\n🔍 CRITICAL COLUMNS CHECK:")
            print("-" * 40)
            
            all_good = True
            for table, column in critical_checks:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s
                """, (table, column))
                exists = cursor.fetchone()
                
                status = "✅" if exists else "❌"
                print(f"{status} {table}.{column}")
                
                if not exists:
                    all_good = False
            
            print("-" * 40)
            if all_good:
                print("🎉 All critical columns exist!")
            else:
                print("⚠️  Some critical columns missing!")
                
    except Exception as e:
        logger.error(f"❌ Column verification failed: {e}")

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--fix-schema":
        print("Running in schema fix mode...")
        success = fix_schema_issues()
        if not success:
            sys.exit(1)
    else:
        print("Starting challenges.one comprehensive database setup...")
        success = init_cloud_database()
        if success:
            print("\n🎯 SETUP COMPLETED SUCCESSFULLY!")
            print("Your challenges.one Strategic Intelligence Platform is ready!")
        else:
            print("\n💥 SETUP FAILED!")
            print("Please check the logs above for details.")
            sys.exit(1)
            
    print("\n📋 Usage Options:")
    print("  python init_cloud_database.py           # Full setup")
    print("  python init_cloud_database.py --fix-schema  # Fix schema only") 