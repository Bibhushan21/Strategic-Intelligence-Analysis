#!/usr/bin/env python3
"""
Cloud Database Rating Tables Initialization Script.
This script adds rating and review tables to the cloud database.
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

def init_cloud_rating_tables():
    """
    Initialize cloud database rating tables if they don't exist.
    """
    try:
        logger.info("Starting cloud rating tables initialization...")
        
        # Import database components
        from data.database_config import engine, test_connection, Base
        from data.models import AgentRating, AgentRatingSummary
        
        # Test connection first
        logger.info("Testing cloud database connection...")
        if not test_connection():
            logger.error("Cloud database connection failed!")
            return False
        
        logger.info("Cloud database connection successful!")
        
        # Check if rating tables already exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        rating_tables_exist = 'agent_ratings' in existing_tables and 'agent_rating_summaries' in existing_tables
        
        if rating_tables_exist:
            logger.info("Rating tables already exist in cloud database")
            return True
        
        # Create rating tables
        logger.info("Creating agent rating tables...")
        
        # Create agent_ratings table
        logger.info("Creating agent_ratings table...")
        AgentRating.__table__.create(engine, checkfirst=True)
        logger.info("✅ agent_ratings table created successfully")
        
        # Create agent_rating_summaries table
        logger.info("Creating agent_rating_summaries table...")
        AgentRatingSummary.__table__.create(engine, checkfirst=True)
        logger.info("✅ agent_rating_summaries table created successfully")
        
        logger.info("Cloud rating tables initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Cloud rating tables initialization failed: {str(e)}")
        logger.exception("Full traceback:")
        return False

def verify_rating_tables():
    """
    Verify that rating tables were created correctly.
    """
    try:
        logger.info("Verifying rating tables...")
        
        from data.database_config import get_db_session, close_db_session
        from data.models import AgentRating, AgentRatingSummary
        
        session = get_db_session()
        
        # Test basic queries on both tables
        rating_count = session.query(AgentRating).count()
        summary_count = session.query(AgentRatingSummary).count()
        
        logger.info(f"agent_ratings table: {rating_count} records")
        logger.info(f"agent_rating_summaries table: {summary_count} records")
        
        close_db_session(session)
        logger.info("✅ Rating tables verification successful!")
        return True
        
    except Exception as e:
        logger.error(f"Rating tables verification failed: {str(e)}")
        return False

def populate_initial_rating_summaries():
    """
    Create initial rating summary entries for all agents.
    """
    try:
        logger.info("Creating initial rating summaries for all agents...")
        
        from data.database_service import DatabaseService
        
        # List of all agents
        agents = [
            'Problem Explorer',
            'Best Practices',
            'Horizon Scanning',
            'Scenario Planning',
            'Research Synthesis',
            'Strategic Action',
            'High Impact',
            'Backcasting'
        ]
        
        for agent_name in agents:
            # This will create or update the rating summary for each agent
            DatabaseService._update_rating_summary(agent_name)
            logger.info(f"✅ Initialized rating summary for {agent_name}")
        
        logger.info("Initial rating summaries created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create initial rating summaries: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Strategic Intelligence App - Cloud Rating Tables Initialization")
    print("=" * 70)
    
    # Step 1: Initialize rating tables
    success = init_cloud_rating_tables()
    if not success:
        print("❌ Cloud rating tables initialization failed!")
        sys.exit(1)
    
    # Step 2: Verify tables
    verify_success = verify_rating_tables()
    if not verify_success:
        print("❌ Rating tables verification failed!")
        sys.exit(1)
    
    # Step 3: Populate initial summaries
    populate_success = populate_initial_rating_summaries()
    if not populate_success:
        print("⚠️ Warning: Could not create initial rating summaries")
    
    print("✅ Cloud rating tables initialization completed successfully!")
    print("\nRating system is now ready for:")
    print("  • User reviews and ratings")
    print("  • Agent performance tracking")
    print("  • Rating analytics and summaries") 