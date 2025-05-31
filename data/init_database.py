#!/usr/bin/env python3
"""
Database initialization script for Strategic Intelligence App.
This script creates all database tables and tests the connection.
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize the database by creating all tables.
    """
    try:
        logger.info("Starting database initialization...")
        
        # Import database components
        from database_config import engine, test_connection, Base
        from models import (
            AnalysisSession, AgentResult, AnalysisTemplate,
            SystemLog, AgentPerformance
        )
        
        # Test connection first
        logger.info("Testing database connection...")
        if not test_connection():
            logger.error("Database connection failed! Please check your connection settings.")
            return False
        
        logger.info("Database connection successful!")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully!")
        
        # Insert sample templates
        logger.info("Creating sample analysis templates...")
        create_sample_templates()
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Make sure all required packages are installed: pip install sqlalchemy psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def create_sample_templates():
    """
    Create some sample analysis templates.
    """
    try:
        from database_service import DatabaseService
        from database_config import get_db_session, close_db_session
        from models import AnalysisTemplate
        
        session = get_db_session()
        
        # Check if templates already exist
        existing_count = session.query(AnalysisTemplate).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing templates, skipping sample creation")
            close_db_session(session)
            return
        
        templates = [
            {
                'name': 'Market Entry Strategy',
                'description': 'Comprehensive analysis for entering new markets',
                'strategic_question_template': 'What are the key considerations and strategic approach for entering the {market} market in {region}?',
                'default_time_frame': '12-18 months',
                'default_region': 'Global',
                'default_instructions': 'Focus on competitive landscape, regulatory environment, and market dynamics'
            },
            {
                'name': 'Technology Disruption Analysis',
                'description': 'Analysis of emerging technology impacts',
                'strategic_question_template': 'How will {technology} disrupt our industry and what strategic responses should we consider?',
                'default_time_frame': '3-5 years',
                'default_region': 'Global',
                'default_instructions': 'Emphasize technological trends, competitive implications, and adaptation strategies'
            },
            {
                'name': 'Geopolitical Risk Assessment',
                'description': 'Assessment of geopolitical risks and opportunities',
                'strategic_question_template': 'What are the geopolitical risks and opportunities in {region} that could impact our strategic objectives?',
                'default_time_frame': '1-3 years',
                'default_region': 'To be specified',
                'default_instructions': 'Consider political stability, trade policies, and regional conflicts'
            },
            {
                'name': 'Sustainability Strategy',
                'description': 'Strategic approach to sustainability and ESG',
                'strategic_question_template': 'How should we develop our sustainability strategy to meet ESG requirements and market expectations?',
                'default_time_frame': '5-10 years',
                'default_region': 'Global',
                'default_instructions': 'Include environmental impact, social responsibility, and governance considerations'
            }
        ]
        
        for template_data in templates:
            template = AnalysisTemplate(**template_data)
            session.add(template)
        
        session.commit()
        logger.info(f"Created {len(templates)} sample analysis templates")
        close_db_session(session)
        
    except Exception as e:
        logger.error(f"Failed to create sample templates: {str(e)}")

def test_database_operations():
    """
    Test basic database operations.
    """
    try:
        logger.info("Testing database operations...")
        
        from database_service import DatabaseService
        
        # Test creating a session
        session_id = DatabaseService.create_analysis_session(
            strategic_question="Test question for database initialization",
            time_frame="Test timeframe",
            region="Test region",
            additional_instructions="This is a test session created during database initialization"
        )
        
        if session_id:
            logger.info(f"Successfully created test session with ID: {session_id}")
            
            # Test saving an agent result
            result_id = DatabaseService.save_agent_result(
                session_id=session_id,
                agent_name="Test Agent",
                agent_type="Test",
                raw_response="Test raw response",
                formatted_output="# Test Output\nThis is a test result.",
                processing_time=1.5
            )
            
            if result_id:
                logger.info(f"Successfully created test agent result with ID: {result_id}")
            
            # Test updating session status
            DatabaseService.update_session_status(session_id, "completed", 5.0)
            logger.info("Successfully updated session status")
            
            # Test retrieving the session
            session_data = DatabaseService.get_analysis_session(session_id)
            if session_data:
                logger.info("Successfully retrieved session data")
            
            logger.info("All database operations test completed successfully!")
            return True
        else:
            logger.error("Failed to create test session")
            return False
            
    except Exception as e:
        logger.error(f"Database operations test failed: {str(e)}")
        return False

def main():
    """
    Main function to run database initialization.
    """
    print("=" * 60)
    print("Strategic Intelligence App - Database Initialization")
    print("=" * 60)
    print()
    
    success = init_database()
    
    if success:
        print("✅ Database initialization completed successfully!")
        
        # Run basic tests
        test_success = test_database_operations()
        if test_success:
            print("✅ Database operations test completed successfully!")
        else:
            print("❌ Database operations test failed!")
            
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)
    
    print()
    print("Database is ready for use!")
    print("You can now run your Strategic Intelligence App.")

if __name__ == "__main__":
    main() 