# Quick Start Guide - AI Website Analyzer

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- MongoDB (local or Atlas)
- Redis (optional for full features)
- Google Gemini API key

## 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
# Copy example env
cp .env.example .env
```

Edit `.env` and set these **REQUIRED** variables:

```env
# MongoDB - Use local or Atlas
MONGODB_URL="mongodb://localhost:27017"
# OR for Atlas:
# MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"

# Google Gemini API (Get from: https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY="your-gemini-api-key-here"

# JWT Secrets (Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY="your-secret-key-here"
JWT_SECRET_KEY="your-jwt-secret-here"
```

**Optional** (for PDF storage):
```env
# Google Drive (See GOOGLE_DRIVE_SETUP.md for details)
GOOGLE_DRIVE_CREDENTIALS_FILE="service-account-key.json"
GOOGLE_DRIVE_FOLDER_ID="your-folder-id"
```

## 3. Start MongoDB (if using local)

```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
net start MongoDB
```

## 4. Seed Sample Users

```bash
python scripts/seed_users.py
```

This creates test accounts:
- **Basic:** basic@example.com / Basic@123
- **Pro:** pro@example.com / Pro@123
- **Enterprise:** enterprise@example.com / Enterprise@123

## 5. Run the Application

### Option A: Simple (without background tasks)

```bash
uvicorn app.main:app --reload
```

### Option B: Full Features (with Celery)

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery
celery -A app.core.celery_app worker --loglevel=info

# Terminal 3: Start FastAPI
uvicorn app.main:app --reload
```

### Option C: Docker (easiest)

```bash
docker-compose up --build
```

## 6. Access the Application

Open your browser:
- **Landing Page:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Login:** http://localhost:8000/login

## 7. Test It Out

### As Guest (No Login)
1. Go to http://localhost:8000/analyze
2. Enter: `https://example.com`
3. Click "Analyze"
4. View results (limited to 1 analysis)

### As Registered User
1. Login with: `basic@example.com` / `Basic@123`
2. Go to /analyze
3. Analyze multiple websites
4. View dashboard at /dashboard
5. Chat with AI about results

## Common Issues

### "Connection refused" to MongoDB
```bash
# Check if MongoDB is running
mongosh  # Should connect successfully

# Or start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod  # Linux
```

### "Invalid API key" for Gemini
- Get a new key from: https://makersuite.google.com/app/apikey
- Make sure you copied it correctly to `.env`
- No quotes needed in `.env` file

### Port 8000 already in use
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Import errors
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Customize branding** - Edit templates in `app/templates/`
2. **Add your logo** - Place in `app/static/images/`
3. **Configure email** - Set SMTP settings in `.env`
4. **Set up Google Drive** - Follow `GOOGLE_DRIVE_SETUP.md`
5. **Deploy to production** - See `SETUP_GUIDE.md`

## Useful Commands

```bash
# Run tests
pytest

# Format code
black app/

# Check code quality
flake8 app/

# View logs
tail -f logs/app.log

# Clean cache
make clean
```

## API Testing

```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123"}'

# Analyze (use token from login)
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"website_url":"https://example.com"}'
```

## Need Help?

- Check `SETUP_GUIDE.md` for detailed instructions
- Review `API_DOCUMENTATION.md` for API details
- See `GOOGLE_DRIVE_SETUP.md` for PDF storage setup
- Open an issue on GitHub

---

**You're all set! Start analyzing websites! 🚀**
