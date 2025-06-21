"""
Migration: Add Agent Rating Tables
Creates the agent_ratings and agent_rating_summaries tables
"""

import sys
import os
from pathlib import Path

# Add the data directory to the path
current_dir = Path(__file__).parent
data_dir = current_dir.parent
sys.path.insert(0, str(data_dir))

from database_config import engine, test_connection, Base
from models import AgentRating, AgentRatingSummary
import logging

logger = logging.getLogger(__name__)

def run_migration():
    """Run the migration to add rating tables"""
    try:
        print("Starting rating tables migration...")
        
        # Test database connection
        if not test_connection():
            print("ERROR: Cannot connect to database")
            return False
        
        print("Database connection successful")
        
        # Create the new tables
        print("Creating agent_ratings table...")
        AgentRating.__table__.create(engine, checkfirst=True)
        print("✓ agent_ratings table created")
        
        print("Creating agent_rating_summaries table...")
        AgentRatingSummary.__table__.create(engine, checkfirst=True)
        print("✓ agent_rating_summaries table created")
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        logger.error(f"Migration failed: {str(e)}")
        return False

def rollback_migration():
    """Rollback the migration by dropping the rating tables"""
    try:
        print("Starting rollback of rating tables migration...")
        
        # Test database connection
        if not test_connection():
            print("ERROR: Cannot connect to database")
            return False
        
        print("Database connection successful")
        
        # Drop the tables (in reverse order due to foreign keys)
        print("Dropping agent_rating_summaries table...")
        AgentRatingSummary.__table__.drop(engine, checkfirst=True)
        print("✓ agent_rating_summaries table dropped")
        
        print("Dropping agent_ratings table...")
        AgentRating.__table__.drop(engine, checkfirst=True)
        print("✓ agent_ratings table dropped")
        
        print("Rollback completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Rollback failed: {str(e)}")
        logger.error(f"Rollback failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration() 