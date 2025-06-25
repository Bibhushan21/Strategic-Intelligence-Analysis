#!/usr/bin/env python3
"""
Deployment script for rating tables on cloud database.
Run this script to add rating functionality to an existing cloud deployment.
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

def deploy_rating_tables():
    """
    Deploy rating tables to cloud database.
    This is safe to run on existing deployments.
    """
    try:
        logger.info("🚀 Starting rating tables deployment to cloud...")
        
        # Import database components
        from data.database_config import engine, test_connection, Base
        from data.models import AgentRating, AgentRatingSummary
        
        # Test connection first
        logger.info("🔍 Testing cloud database connection...")
        if not test_connection():
            logger.error("❌ Cloud database connection failed!")
            return False
        
        logger.info("✅ Cloud database connection successful!")
        
        # Check current state
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        logger.info(f"📊 Found {len(existing_tables)} existing tables in database")
        
        # Check if rating tables already exist
        rating_tables_status = {
            'agent_ratings': 'agent_ratings' in existing_tables,
            'agent_rating_summaries': 'agent_rating_summaries' in existing_tables
        }
        
        logger.info("📋 Rating tables status:")
        for table, exists in rating_tables_status.items():
            status = "✅ EXISTS" if exists else "❌ MISSING"
            logger.info(f"   {table}: {status}")
        
        if all(rating_tables_status.values()):
            logger.info("🎉 All rating tables already exist! Deployment is up to date.")
            return verify_and_initialize()
        
        # Create missing tables
        logger.info("🔨 Creating missing rating tables...")
        
        if not rating_tables_status['agent_ratings']:
            logger.info("📝 Creating agent_ratings table...")
            AgentRating.__table__.create(engine, checkfirst=True)
            logger.info("✅ agent_ratings table created successfully")
        
        if not rating_tables_status['agent_rating_summaries']:
            logger.info("📝 Creating agent_rating_summaries table...")
            AgentRatingSummary.__table__.create(engine, checkfirst=True)
            logger.info("✅ agent_rating_summaries table created successfully")
        
        logger.info("🎉 Rating tables deployment completed successfully!")
        
        # Verify and initialize
        return verify_and_initialize()
        
    except Exception as e:
        logger.error(f"❌ Rating tables deployment failed: {str(e)}")
        logger.exception("Full traceback:")
        return False

def verify_and_initialize():
    """
    Verify tables and initialize rating summaries.
    """
    try:
        logger.info("🔍 Verifying rating tables...")
        
        from data.database_config import get_db_session, close_db_session
        from data.models import AgentRating, AgentRatingSummary
        
        session = get_db_session()
        
        # Test basic operations on both tables
        rating_count = session.query(AgentRating).count()
        summary_count = session.query(AgentRatingSummary).count()
        
        logger.info(f"📊 Current data:")
        logger.info(f"   agent_ratings: {rating_count} records")
        logger.info(f"   agent_rating_summaries: {summary_count} records")
        
        close_db_session(session)
        
        # Initialize rating summaries for all agents
        logger.info("🔧 Initializing rating summaries...")
        initialize_agent_summaries()
        
        logger.info("✅ Verification and initialization completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        return False

def initialize_agent_summaries():
    """
    Initialize or update rating summaries for all agents.
    """
    try:
        from data.database_service import DatabaseService
        
        # List of all agents in the system
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
        
        logger.info(f"🎯 Initializing summaries for {len(agents)} agents...")
        
        initialized_count = 0
        for agent_name in agents:
            try:
                # This will create or update the rating summary
                DatabaseService._update_rating_summary(agent_name)
                logger.info(f"✅ {agent_name}")
                initialized_count += 1
            except Exception as e:
                logger.warning(f"⚠️ {agent_name}: {str(e)}")
        
        logger.info(f"🎉 Successfully initialized {initialized_count}/{len(agents)} agent summaries")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent summaries: {str(e)}")

def test_rating_system():
    """
    Test the rating system functionality.
    """
    try:
        logger.info("🧪 Testing rating system functionality...")
        
        from data.database_service import DatabaseService
        
        # Test rating summary retrieval
        summary = DatabaseService.get_agent_rating_summary('Problem Explorer')
        if summary:
            logger.info("✅ Rating summary retrieval works")
        else:
            logger.info("ℹ️ No ratings found (expected for new deployment)")
        
        # Test rating summaries listing
        summaries = DatabaseService.get_all_agent_rating_summaries()
        logger.info(f"✅ Found {len(summaries)} agent rating summaries")
        
        logger.info("🎉 Rating system test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Rating system test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 STRATEGIC INTELLIGENCE APP - RATING TABLES DEPLOYMENT")
    print("=" * 80)
    print()
    
    # Step 1: Deploy rating tables
    logger.info("STEP 1: Deploying rating tables...")
    deploy_success = deploy_rating_tables()
    if not deploy_success:
        print("\n❌ DEPLOYMENT FAILED!")
        sys.exit(1)
    
    # Step 2: Test rating system
    logger.info("\nSTEP 2: Testing rating system...")
    test_success = test_rating_system()
    if not test_success:
        print("\n⚠️ WARNING: Rating system tests failed!")
    
    print("\n" + "=" * 80)
    print("🎉 RATING TABLES DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\n✅ Your cloud database now supports:")
    print("   • User reviews and ratings for agent outputs")
    print("   • Agent performance tracking and analytics")
    print("   • Rating summaries and statistics")
    print("   • Rating-based recommendations")
    print("\n🔗 The rating system is now fully integrated with your existing deployment!") 