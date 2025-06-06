# Render Environment Variables Setup

When deploying to Render, set these environment variables in your Render dashboard:

## Database Configuration (Option 1 - Individual variables)
```
DB_HOST=dpg-d11b1u95pdvs73eq2kf0-a.frankfurt-postgres.render.com
DB_PORT=5432
DB_NAME=strategicintelligenceanalysis_db
DB_USER=strategicintelligenceanalysis_db_user
DB_PASSWORD=Gzan5HtrMLr5sv0zszmRT0eAK6GDajBO
```

## Database Configuration (Option 2 - Single URL - RECOMMENDED)
```
DATABASE_URL=postgresql://strategicintelligenceanalysis_db_user:Gzan5HtrMLr5sv0zszmRT0eAK6GDajBO@dpg-d11b1u95pdvs73eq2kf0-a.frankfurt-postgres.render.com/strategicintelligenceanalysis_db
```

## How to set these in Render:

1. Go to your Render Dashboard
2. Select your web service
3. Go to the "Environment" tab
4. Add the environment variable(s) above
5. Click "Save Changes"
6. Your service will automatically redeploy with the new database connection

## Local Development:
- Your local development will continue to use the localhost PostgreSQL database
- No changes needed for local development

## Notes:
- The app will automatically use the cloud database when `DATABASE_URL` is set
- For local development, it falls back to your local PostgreSQL settings
- The app handles both `postgres://` and `postgresql://` URL formats automatically 