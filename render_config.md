# Render Deployment Configuration

## Updated Requirements
The `requirements.txt` has been updated with all necessary dependencies including:
- `gunicorn` for production server
- `psycopg2-binary` for PostgreSQL connection  
- Database dependencies (`sqlalchemy`, `sqlalchemy-utils`)

## Render Service Settings

### Build Command
```
pip install -r requirements.txt
```

### Start Command (Option 1 - With Database Init - RECOMMENDED)
```
bash start.sh
```

### Start Command (Option 2 - Direct start)
```
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Environment Variables
Set this in your Render Environment tab:
```
DATABASE_URL=postgresql://strategicintelligenceanalysis_db_user:Gzan5HtrMLr5sv0zszmRT0eAK6GDajBO@dpg-d11b1u95pdvs73eq2kf0-a.frankfurt-postgres.render.com/strategicintelligenceanalysis_db
```

## Database Initialization
The app now includes automatic database table creation:

1. **Database tables will be created automatically** when the app starts
2. **Sample templates** will be added if none exist
3. **Backup initialization** happens on FastAPI startup event

### Manual Database Initialization (if needed)
If you want to initialize the database manually:
```bash
python init_cloud_database.py
```

## Deployment Steps

1. **Update your code** - Push all updated files to your repository:
   - Updated `requirements.txt` 
   - New `init_cloud_database.py`
   - Updated `start.sh`
   - Updated `app/main.py` with startup event

2. **In Render Dashboard:**
   - Go to your Web Service
   - Settings → Build & Deploy
   - Set Build Command: `pip install -r requirements.txt`
   - Set Start Command: `bash start.sh` (RECOMMENDED)
3. **Environment Tab:**
   - Add the `DATABASE_URL` environment variable
4. **Deploy** - Click "Manual Deploy" or push to trigger auto-deploy

## What This Fixes

✅ **Database Tables**: All required tables (`analysis_sessions`, `agent_results`, etc.) will be created automatically

✅ **Frontend Updates**: Agent results will now be properly saved and displayed 

✅ **Error Handling**: Better error handling for database operations

✅ **Sample Data**: Sample templates created for immediate use

## Troubleshooting

### If you still get database errors:
1. Check that `DATABASE_URL` environment variable is set correctly
2. Verify PostgreSQL database is accessible
3. Check application logs for database connection issues

### If frontend still doesn't update:
1. Check browser developer console for JavaScript errors
2. Verify that analysis results are being saved to database
3. Check that WebSocket/streaming connections are working

## File Structure Expected
```
your-repo/
├── app/
│   ├── main.py              # Updated with startup event
│   ├── templates/
│   └── static/
├── data/
│   ├── database_config.py   # Updated with env vars
│   ├── models.py           # Database models
│   ├── database_service.py # Database operations
│   └── init_database.py    # Local initialization
├── init_cloud_database.py   # NEW: Cloud initialization
├── requirements.txt         # Updated with all deps
├── start.sh                # Updated with DB init
└── render_config.md        # This file
``` 