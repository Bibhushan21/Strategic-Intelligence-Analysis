#!/usr/bin/env python3
"""
Cloud Database Initialization Script for Render Deployment.
This script initializes the database tables on first run.
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

def init_cloud_database():
    """
    Initialize cloud database tables if they don't exist.
    """
    try:
        logger.info("Starting cloud database initialization...")
        
        # Import database components
        from data.database_config import engine, test_connection, Base
        from data.models import (
            AnalysisSession, AgentResult, AnalysisTemplate,
            SystemLog, AgentPerformance
        )
        
        # Test connection first
        logger.info("Testing cloud database connection...")
        if not test_connection():
            logger.error("Cloud database connection failed!")
            return False
        
        logger.info("Cloud database connection successful!")
        
        # Create all tables (this is safe - won't recreate existing tables)
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created/verified successfully!")
        
        # Create sample templates if none exist
        try:
            create_sample_templates_if_needed()
        except Exception as e:
            logger.warning(f"Could not create sample templates: {e}")
        
        logger.info("Cloud database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Cloud database initialization failed: {str(e)}")
        return False

def create_sample_templates_if_needed():
    """
    Create sample templates only if none exist.
    """
    try:
        from data.database_config import get_db_session, close_db_session
        from data.models import AnalysisTemplate
        
        session = get_db_session()
        
        # Check if templates already exist
        existing_count = session.query(AnalysisTemplate).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing templates, skipping sample creation")
            close_db_session(session)
            return
        
        logger.info("Creating sample analysis templates...")
        
        templates = [
            {
                'name': 'Market Entry Strategy',
                'description': 'Comprehensive analysis for entering new markets',
                'strategic_question_template': 'What are the key considerations and strategic approach for entering the {market} market in {region}?',
                'default_time_frame': 'medium_term',
                'default_region': 'global',
                'default_instructions': 'Focus on competitive landscape, regulatory environment, and market dynamics'
            },
            {
                'name': 'Technology Disruption Analysis', 
                'description': 'Analysis of emerging technology impacts',
                'strategic_question_template': 'How will {technology} disrupt our industry and what strategic responses should we consider?',
                'default_time_frame': 'long_term',
                'default_region': 'global',
                'default_instructions': 'Emphasize technological trends, competitive implications, and adaptation strategies'
            },
            {
                'name': 'EV Industry Analysis',
                'description': 'Electric Vehicle industry market analysis',
                'strategic_question_template': 'What are the key market opportunities and strategic considerations for EV Industry? Analyze market dynamics, competitive landscape, entry strategies, and growth potential.',
                'default_time_frame': 'long_term',
                'default_region': 'asia',
                'default_instructions': 'Focus on technological advances, infrastructure development, and market penetration strategies'
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

if __name__ == "__main__":
    print("=" * 60)
    print("Strategic Intelligence App - Cloud Database Initialization")
    print("=" * 60)
    
    success = init_cloud_database()
    if success:
        print("✅ Cloud database initialization completed successfully!")
    else:
        print("❌ Cloud database initialization failed!")
        sys.exit(1) 