#!/usr/bin/env python3
"""
Template Table Migration Script
Adds missing columns to the analysis_templates table in cloud database.
"""

import os
import sys
import logging
from pathlib import Path

# Add data directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'data'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def migrate_template_table():
    """
    Add missing columns to the analysis_templates table.
    """
    try:
        logger.info("🚀 Starting template table migration...")
        
        # Import database components
        from data.database_config import engine, test_connection, get_db_session, close_db_session
        from sqlalchemy import text, inspect
        
        # Test connection first
        logger.info("🔍 Testing cloud database connection...")
        if not test_connection():
            logger.error("❌ Cloud database connection failed!")
            return False
        
        logger.info("✅ Cloud database connection successful!")
        
        # Check current table structure
        inspector = inspect(engine)
        
        # Check if analysis_templates table exists
        if 'analysis_templates' not in inspector.get_table_names():
            logger.error("❌ analysis_templates table does not exist!")
            return False
        
        logger.info("✅ analysis_templates table found")
        
        # Get current columns
        current_columns = [col['name'] for col in inspector.get_columns('analysis_templates')]
        logger.info(f"📋 Current columns: {current_columns}")
        
        # Define required columns and their SQL
        required_columns = {
            'category': 'VARCHAR(100) DEFAULT \'General\'',
            'tags': 'JSON',
            'is_public': 'BOOLEAN DEFAULT TRUE',
            'created_by': 'VARCHAR(100) DEFAULT \'system\''
        }
        
        session = get_db_session()
        
        # Add missing columns
        for column_name, column_definition in required_columns.items():
            if column_name not in current_columns:
                logger.info(f"📝 Adding column: {column_name}")
                try:
                    alter_sql = f"ALTER TABLE analysis_templates ADD COLUMN {column_name} {column_definition}"
                    session.execute(text(alter_sql))
                    session.commit()
                    logger.info(f"✅ Added column: {column_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to add column {column_name}: {str(e)}")
                    session.rollback()
            else:
                logger.info(f"✅ Column {column_name} already exists")
        
        close_db_session(session)
        
        # Verify the migration
        logger.info("🔍 Verifying migration...")
        return verify_migration()
        
    except Exception as e:
        logger.error(f"❌ Template table migration failed: {str(e)}")
        logger.exception("Full traceback:")
        return False

def verify_migration():
    """
    Verify that all required columns exist.
    """
    try:
        from data.database_config import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        current_columns = [col['name'] for col in inspector.get_columns('analysis_templates')]
        
        required_columns = ['category', 'tags', 'is_public', 'created_by']
        
        missing_columns = [col for col in required_columns if col not in current_columns]
        
        if missing_columns:
            logger.error(f"❌ Still missing columns: {missing_columns}")
            return False
        
        logger.info("✅ All required columns are present!")
        logger.info(f"📋 Final columns: {current_columns}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {str(e)}")
        return False

def update_existing_templates():
    """
    Update existing templates with default categories.
    """
    try:
        logger.info("🔧 Updating existing templates...")
        
        from data.database_config import get_db_session, close_db_session
        from sqlalchemy import text
        
        session = get_db_session()
        
        # Update templates without categories
        category_mappings = {
            'Market Entry Strategy': 'Business Strategy',
            'Technology Disruption Analysis': 'Technology',
            'EV Industry Analysis': 'Industry Analysis',
            'Competitive Analysis': 'Business Strategy',
            'Risk Assessment': 'Risk Management',
            'Digital Transformation': 'Technology'
        }
        
        # First, set default category for all templates
        session.execute(text("""
            UPDATE analysis_templates 
            SET category = 'General' 
            WHERE category IS NULL OR category = ''
        """))
        
        # Update specific templates based on their names
        for template_name, category in category_mappings.items():
            session.execute(text("""
                UPDATE analysis_templates 
                SET category = :category 
                WHERE name LIKE :name
            """), {'category': category, 'name': f'%{template_name}%'})
        
        session.commit()
        close_db_session(session)
        
        logger.info("✅ Existing templates updated!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update existing templates: {str(e)}")
        return False

def test_template_functionality():
    """
    Test template functionality after migration.
    """
    try:
        logger.info("🧪 Testing template functionality...")
        
        from data.database_service import DatabaseService
        
        # Test getting templates
        templates = DatabaseService.get_templates(limit=5)
        logger.info(f"✅ Retrieved {len(templates)} templates")
        
        # Test getting categories
        categories = DatabaseService.get_template_categories()
        logger.info(f"✅ Retrieved {len(categories)} categories")
        
        if categories:
            logger.info(f"📋 Available categories: {[cat['category'] for cat in categories]}")
        
        logger.info("🎉 Template functionality test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Template functionality test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 TEMPLATE TABLE MIGRATION")
    print("=" * 80)
    print()
    
    # Step 1: Migrate table structure
    logger.info("STEP 1: Migrating table structure...")
    migrate_success = migrate_template_table()
    if not migrate_success:
        print("\n❌ MIGRATION FAILED!")
        sys.exit(1)
    
    # Step 2: Update existing templates
    logger.info("\nSTEP 2: Updating existing templates...")
    update_success = update_existing_templates()
    if not update_success:
        print("\n⚠️ WARNING: Could not update existing templates")
    
    # Step 3: Test functionality
    logger.info("\nSTEP 3: Testing template functionality...")
    test_success = test_template_functionality()
    if not test_success:
        print("\n⚠️ WARNING: Template functionality test failed")
    
    print("\n" + "=" * 80)
    print("🎉 TEMPLATE TABLE MIGRATION COMPLETED!")
    print("=" * 80)
    print("\n✅ Template table now includes:")
    print("   • category - Template categorization")
    print("   • tags - JSON array for better organization")
    print("   • is_public - Public/private template control")
    print("   • created_by - Template creator tracking")
    print("\n🔗 Templates functionality should now work correctly!") 