# Setup Checklist - AI Website Analyzer

Use this checklist to ensure everything is configured correctly.

## ✅ Prerequisites

- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] Code editor (VS Code, PyCharm, etc.)
- [ ] Terminal/Command line access

## ✅ Project Setup

- [ ] Repository cloned
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)

## ✅ Database Setup

### MongoDB
- [ ] MongoDB installed locally OR
- [ ] MongoDB Atlas account created
- [ ] Database connection string obtained
- [ ] Connection string added to `.env`
- [ ] Connection tested (can connect successfully)

### Redis (Optional but recommended)
- [ ] Redis installed locally OR
- [ ] Redis cloud service configured
- [ ] Redis URL added to `.env`

## ✅ API Keys & Credentials

### Google Gemini API (REQUIRED)
- [ ] Visited https://makersuite.google.com/app/apikey
- [ ] Created API key
- [ ] Added `GOOGLE_API_KEY` to `.env`
- [ ] Tested API key works

### Google Drive API (OPTIONAL - for PDF storage)
- [ ] Created Google Cloud Project
- [ ] Enabled Google Drive API
- [ ] Created Service Account
- [ ] Downloaded `service-account-key.json`
- [ ] Moved key file to project root
- [ ] Created Google Drive folder
- [ ] Copied folder ID
- [ ] Shared folder with service account email
- [ ] Added `GOOGLE_DRIVE_FOLDER_ID` to `.env`

## ✅ Environment Configuration

- [ ] Copied `.env.example` to `.env`
- [ ] Set `MONGODB_URL`
- [ ] Set `GOOGLE_API_KEY`
- [ ] Generated and set `SECRET_KEY`
- [ ] Generated and set `JWT_SECRET_KEY`
- [ ] Set `REDIS_URL` (if using Redis)
- [ ] Set Google Drive credentials (if using)
- [ ] Reviewed all other settings

### Generate Secure Keys
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## ✅ Sample Data

- [ ] Ran seed script: `python scripts/seed_users.py`
- [ ] Verified test accounts created:
  - [ ] basic@example.com / Basic@123
  - [ ] pro@example.com / Pro@123
  - [ ] enterprise@example.com / Enterprise@123

## ✅ Application Startup

### Option 1: Simple (No background tasks)
- [ ] Started application: `uvicorn app.main:app --reload`
- [ ] Application running on http://localhost:8000
- [ ] Can access landing page
- [ ] Can access API docs at /docs

### Option 2: Full Features (With Celery)
- [ ] Started Redis: `redis-server`
- [ ] Started Celery: `celery -A app.core.celery_app worker --loglevel=info`
- [ ] Started FastAPI: `uvicorn app.main:app --reload`
- [ ] All services running

### Option 3: Docker
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Ran: `docker-compose up --build`
- [ ] All containers running
- [ ] Application accessible

## ✅ Testing

### Manual Testing
- [ ] Opened http://localhost:8000
- [ ] Landing page loads correctly
- [ ] Clicked "Analyze Your Website"
- [ ] Entered test URL (https://example.com)
- [ ] Analysis started successfully
- [ ] Results page displayed
- [ ] Scores visible
- [ ] AI summary generated

### Authentication Testing
- [ ] Clicked "Login"
- [ ] Logged in with: basic@example.com / Basic@123
- [ ] Redirected to dashboard
- [ ] Dashboard shows user info
- [ ] Can access analyze page
- [ ] Can perform multiple analyses

### API Testing
- [ ] Accessed http://localhost:8000/docs
- [ ] Swagger UI loads
- [ ] Can see all endpoints
- [ ] Tried "Try it out" on /health endpoint
- [ ] Health check returns success

### Automated Testing
- [ ] Ran: `pytest`
- [ ] All tests pass

## ✅ Features Verification

### Guest User (No Login)
- [ ] Can analyze 1 website
- [ ] Gets rate limited after 1 analysis
- [ ] Sees "Please register" message

### Registered User
- [ ] Can login successfully
- [ ] Dashboard shows stats
- [ ] Can perform multiple analyses (based on plan)
- [ ] Can view analysis history
- [ ] Can chat with AI about results
- [ ] Can download PDF (if Drive configured)

### Analysis Features
- [ ] UX analysis works
- [ ] SEO analysis works
- [ ] Performance analysis works
- [ ] Content analysis works
- [ ] Overall score calculated
- [ ] AI summary generated
- [ ] Priority recommendations shown
- [ ] Charts display correctly

## ✅ Documentation Review

- [ ] Read README.md
- [ ] Read QUICK_START.md
- [ ] Reviewed SETUP_GUIDE.md
- [ ] Checked API_DOCUMENTATION.md
- [ ] Reviewed SAMPLE_CREDENTIALS.md
- [ ] Understood WORKFLOW_DIAGRAM.md

## ✅ Customization (Optional)

- [ ] Updated app name in templates
- [ ] Added custom logo
- [ ] Changed color scheme (if desired)
- [ ] Updated footer information
- [ ] Customized email templates
- [ ] Modified pricing plans

## ✅ Production Preparation (When Ready)

- [ ] Set `ENVIRONMENT=production` in .env
- [ ] Set `DEBUG=False`
- [ ] Used strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configured proper CORS origins
- [ ] Set up SSL certificates
- [ ] Configured production MongoDB cluster
- [ ] Set up Redis persistence
- [ ] Configured email service
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configured backups
- [ ] Set up CI/CD pipeline

## ✅ Security Checklist

- [ ] `.env` file in `.gitignore`
- [ ] `service-account-key.json` in `.gitignore`
- [ ] Strong passwords for test accounts
- [ ] JWT secrets are random and secure
- [ ] MongoDB connection uses authentication
- [ ] Redis password set (if exposed)
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Input validation working

## 🎯 Next Steps

Once everything is checked:

1. **Customize the application**
   - Update branding
   - Modify templates
   - Adjust pricing

2. **Add more features**
   - Implement PDF generation
   - Add email notifications
   - Create more analysis modules

3. **Deploy to production**
   - Choose hosting provider
   - Set up domain
   - Configure SSL
   - Deploy with Docker

4. **Monitor and maintain**
   - Set up logging
   - Monitor errors
   - Track usage
   - Gather feedback

## 📞 Need Help?

If you're stuck on any item:

1. Check the relevant documentation file
2. Review error messages carefully
3. Check logs: `docker-compose logs -f` or terminal output
4. Verify environment variables are set correctly
5. Ensure all services are running
6. Try restarting services
7. Check GitHub issues
8. Open a new issue with details

## ✨ Success Indicators

You're ready to go when:

- ✅ Application starts without errors
- ✅ Can access all pages
- ✅ Can perform analysis as guest
- ✅ Can login and use dashboard
- ✅ Analysis completes successfully
- ✅ AI chat works
- ✅ All test accounts work
- ✅ API documentation accessible

---

**Congratulations! You're all set! 🎉**

Start analyzing websites and helping businesses grow!
