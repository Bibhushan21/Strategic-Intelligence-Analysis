# 🌟 Rating System Cloud Deployment Guide

This guide explains how to deploy the rating and review system to your cloud database.

## 📋 Overview

The rating system consists of two main database tables:
- **`agent_ratings`** - Stores individual user ratings and reviews
- **`agent_rating_summaries`** - Stores aggregated statistics for each agent

## 🚀 Deployment Options

### Option 1: Full Deployment Script (Recommended)
Use this for new deployments or when you want a comprehensive setup:

```bash
python deploy_rating_tables.py
```

**What it does:**
- ✅ Tests cloud database connection
- ✅ Checks existing table status
- ✅ Creates missing rating tables
- ✅ Verifies table functionality
- ✅ Initializes rating summaries for all agents
- ✅ Tests the rating system

### Option 2: Standalone Rating Tables Only
Use this if you just need the tables without initialization:

```bash
python init_cloud_rating_tables.py
```

**What it does:**
- ✅ Creates rating tables
- ✅ Verifies tables work correctly
- ✅ Initializes basic rating summaries

### Option 3: Update Main Initialization
If you want rating tables included in your main deployment process, the updated `init_cloud_database.py` now includes rating tables automatically.

```bash
python init_cloud_database.py
```

## 📊 Database Schema

### agent_ratings Table
```sql
CREATE TABLE agent_ratings (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES analysis_sessions(id),
    agent_result_id INTEGER NOT NULL REFERENCES agent_results(id),
    agent_name VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) DEFAULT 'anonymous',
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    helpful_aspects JSON,
    improvement_suggestions TEXT,
    would_recommend BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### agent_rating_summaries Table
```sql
CREATE TABLE agent_rating_summaries (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    total_ratings INTEGER DEFAULT 0,
    average_rating FLOAT DEFAULT 0.0,
    five_star_count INTEGER DEFAULT 0,
    four_star_count INTEGER DEFAULT 0,
    three_star_count INTEGER DEFAULT 0,
    two_star_count INTEGER DEFAULT 0,
    one_star_count INTEGER DEFAULT 0,
    total_reviews INTEGER DEFAULT 0,
    recommendation_percentage FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 Environment Setup

### Required Environment Variables

For cloud deployment, ensure these environment variables are set:

```bash
# PostgreSQL Database URL (for cloud deployment)
DATABASE_URL=postgresql://username:password@host:port/database

# Or individual components
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-username
DB_PASSWORD=your-password
```

### Dependencies

Ensure these packages are installed:
```bash
pip install sqlalchemy psycopg2-binary python-dotenv
```

## 🧪 Testing the Deployment

After deployment, test the rating system:

```python
from data.database_service import DatabaseService

# Test rating summary retrieval
summary = DatabaseService.get_agent_rating_summary('Problem Explorer')
print(f"Summary: {summary}")

# Test listing all summaries
summaries = DatabaseService.get_all_agent_rating_summaries()
print(f"Found {len(summaries)} agent summaries")
```

## 🔄 Post-Deployment Verification

1. **Check Table Creation:**
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_name IN ('agent_ratings', 'agent_rating_summaries');
   ```

2. **Verify Initial Data:**
   ```sql
   SELECT agent_name, total_ratings, average_rating 
   FROM agent_rating_summaries;
   ```

3. **Test Rating Submission:**
   - Navigate to your app
   - Complete an analysis
   - Submit a rating using the "Review Analysis" button
   - Check the database for the new rating record

## 🚨 Troubleshooting

### Connection Issues
- Verify DATABASE_URL is correct
- Check network connectivity to database
- Ensure database user has CREATE TABLE permissions

### Table Creation Fails
- Check if tables already exist
- Verify database user has proper permissions
- Look for constraint conflicts

### Rating Submission Fails
- Ensure session_id and agent_result_id are being passed correctly
- Check foreign key constraints
- Verify the rating endpoint is accessible

## 📈 Monitoring

After deployment, monitor:
- Rating submission success rates
- Database performance with new tables
- User engagement with the rating system

## 🔄 Updates

To update rating tables in the future:
1. Modify the models in `data/models.py`
2. Create a new migration script
3. Run the migration on your cloud database

## 🎉 Success!

Once deployed, your users can:
- ⭐ Rate agent outputs (1-5 stars)
- 📝 Leave detailed reviews
- 💡 Provide improvement suggestions
- 👍 Indicate if they'd recommend the agent

The system will automatically track and display:
- 📊 Average ratings per agent
- 📈 Rating trends over time
- 🏆 Top-rated agents
- �� Detailed analytics 