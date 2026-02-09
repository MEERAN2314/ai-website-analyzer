# AI Website Analyzer - Setup Guide

## Quick Start Guide

### Prerequisites
- Python 3.11 or higher
- Docker and Docker Compose (recommended)
- MongoDB Atlas account
- Google Gemini API key
- Redis (included in Docker setup)

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-website-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required Configuration:**

1. **MongoDB Atlas:**
   - Create a free cluster at https://www.mongodb.com/cloud/atlas
   - Get connection string
   - Update `MONGODB_URL` in .env

2. **Google Gemini API:**
   - Get API key from https://makersuite.google.com/app/apikey
   - Update `GOOGLE_API_KEY` in .env

3. **JWT Secrets:**
   - Generate secure random strings
   - Update `SECRET_KEY` and `JWT_SECRET_KEY`

```bash
# Generate secure keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Run with Docker (Recommended)

```bash
# Build and start all services
docker-compose up --build

# The application will be available at:
# http://localhost:8000
```

### Step 4: Run Locally (Alternative)

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery Worker
celery -A app.core.celery_app worker --loglevel=info

# Terminal 3: Start FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Seed Sample Users

```bash
# Create test accounts
python scripts/seed_users.py
```

This creates 4 test accounts:
- **Basic:** basic@example.com / Basic@123
- **Pro:** pro@example.com / Pro@123
- **Enterprise:** enterprise@example.com / Enterprise@123
- **Admin:** admin@example.com / Admin@123

### Step 6: Access the Application

1. **Landing Page:** http://localhost:8000
2. **API Docs:** http://localhost:8000/docs
3. **Login:** http://localhost:8000/login
4. **Analyze:** http://localhost:8000/analyze

## Testing the Application

### 1. Guest Analysis (No Login)
- Go to http://localhost:8000/analyze
- Enter any website URL (e.g., https://example.com)
- Click "Analyze"
- View results (limited to 1 analysis)

### 2. Registered User Analysis
- Login with test credentials
- Go to /analyze
- Analyze multiple websites based on plan
- Access dashboard at /dashboard
- View analysis history

### 3. API Testing

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123","full_name":"Test User"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123"}'

# Start analysis (use token from login)
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"website_url":"https://example.com"}'
```

## Project Structure

```
ai-website-analyzer/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core configuration
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   ├── analyzers/            # Analysis modules
│   ├── templates/            # Jinja2 templates
│   ├── static/               # CSS, JS, images
│   └── main.py               # FastAPI app
├── scripts/                  # Utility scripts
├── docker-compose.yml        # Docker configuration
├── Dockerfile                # Docker image
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables
```

## Common Issues & Solutions

### Issue: MongoDB Connection Failed
**Solution:** 
- Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for development)
- Verify connection string format
- Ensure database user has read/write permissions

### Issue: Gemini API Error
**Solution:**
- Verify API key is correct
- Check API quota/limits
- Ensure billing is enabled (if required)

### Issue: Redis Connection Failed
**Solution:**
- Ensure Redis is running: `redis-cli ping`
- Check REDIS_URL in .env
- For Docker: ensure redis service is up

### Issue: Celery Worker Not Processing
**Solution:**
- Check Celery logs for errors
- Verify Redis connection
- Restart Celery worker

### Issue: Port Already in Use
**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

## Development Tips

### Hot Reload
FastAPI automatically reloads on code changes when using `--reload` flag.

### Database Inspection
```bash
# Connect to MongoDB
mongosh "YOUR_MONGODB_URL"

# List databases
show dbs

# Use database
use website_analyzer

# View collections
show collections

# Query users
db.users.find().pretty()
```

### Redis Inspection
```bash
# Connect to Redis
redis-cli

# View all keys
KEYS *

# Get value
GET key_name

# Clear all data
FLUSHALL
```

### Logs
```bash
# View Docker logs
docker-compose logs -f web
docker-compose logs -f celery_worker

# View specific service
docker-compose logs -f redis
```

## Production Deployment

### Environment Variables
- Set `ENVIRONMENT=production`
- Set `DEBUG=False`
- Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- Configure proper CORS origins
- Set up SSL certificates

### Database
- Use MongoDB Atlas production cluster
- Enable authentication
- Set up backups
- Configure connection pooling

### Scaling
- Use multiple Celery workers
- Implement Redis Cluster
- Use load balancer (Nginx)
- Enable caching strategies

### Monitoring
- Set up Sentry for error tracking
- Monitor API response times
- Track analysis queue length
- Set up alerts for failures

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Check logs for errors
4. Open an issue on GitHub

## Next Steps

1. Customize landing page content
2. Add your branding/logo
3. Configure email notifications
4. Set up Google Drive for PDF storage
5. Implement payment integration
6. Add more analysis features
7. Create custom PDF templates

---

**Happy Analyzing! 🚀**
