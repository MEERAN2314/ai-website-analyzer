# 👋 START HERE - AI Website Analyzer

Welcome! This is your starting point for the AI Website Analyzer project.

## 🎯 What is This?

A professional AI-powered tool that analyzes websites and provides actionable recommendations for:
- **UX/UI** improvements
- **SEO** optimization
- **Performance** enhancements
- **Content** quality

## 🚀 I Want to Get Started NOW!

### Super Quick Start (3 Steps)

1. **Install & Configure**
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Add MongoDB URL and Gemini API key
```

2. **Seed & Run**
```bash
python scripts/seed_users.py
uvicorn app.main:app --reload
```

3. **Open & Test**
- Go to: http://localhost:8000
- Login: `basic@example.com` / `Basic@123`
- Analyze a website!

**Need help?** → See [QUICK_START.md](QUICK_START.md)

## 📖 What Should I Read First?

Choose your path:

### 🏃 I Want to Run It Quickly
→ **[QUICK_START.md](QUICK_START.md)** (5 minutes)

### 🔧 I Want Detailed Setup Instructions
→ **[SETUP_GUIDE.md](SETUP_GUIDE.md)** (15 minutes)

### 🔑 I Need to Get API Keys
→ **[GETTING_GOOGLE_CREDENTIALS.md](GETTING_GOOGLE_CREDENTIALS.md)** (10 minutes)

### 📚 I Want to Understand the Project
→ **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** (10 minutes)

### 🔌 I Want to Use the API
→ **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** (Reference)

### 🎨 I Want to See How It Works
→ **[WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md)** (Visual guide)

### ✅ I Want a Step-by-Step Checklist
→ **[CHECKLIST.md](CHECKLIST.md)** (Complete checklist)

## 🎓 What Do I Need?

### Required
- ✅ Python 3.11+
- ✅ MongoDB (local or Atlas)
- ✅ Google Gemini API key

### Optional (but recommended)
- ⭐ Redis (for caching)
- ⭐ Docker (for easy deployment)
- ⭐ Google Drive API (for PDF storage)

## 🔑 Getting API Keys

### Google Gemini API (Required)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Add to `.env`: `GOOGLE_API_KEY="your-key-here"`

**That's it!** The app will work with just this.

### Google Drive API (Optional)
For PDF storage, follow: [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)

## 📁 Project Structure

```
ai-website-analyzer/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   ├── analyzers/         # Analysis modules
│   ├── services/          # Business logic
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, images
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── .env                   # Your configuration
└── [Documentation].md     # All these guides!
```

## 🎮 Test Accounts

After running `python scripts/seed_users.py`:

| Plan | Email | Password |
|------|-------|----------|
| Basic | basic@example.com | Basic@123 |
| Pro | pro@example.com | Pro@123 |
| Enterprise | enterprise@example.com | Enterprise@123 |

## 🌐 Important URLs

Once running:
- **Landing Page**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Login**: http://localhost:8000/login
- **Analyze**: http://localhost:8000/analyze
- **Dashboard**: http://localhost:8000/dashboard

## 🎯 Quick Test Flow

1. **As Guest** (no login):
   - Go to /analyze
   - Enter: `https://example.com`
   - View results (limited to 1 analysis)

2. **As Registered User**:
   - Login with test credentials
   - Analyze multiple websites
   - View dashboard
   - Chat with AI about results

## 🐛 Common Issues

### "Connection refused" to MongoDB
```bash
# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
```

### "Invalid API key" for Gemini
- Get new key from: https://makersuite.google.com/app/apikey
- Copy entire key to `.env`

### Port 8000 already in use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

## 📚 All Documentation Files

| File | Purpose | Time |
|------|---------|------|
| **START_HERE.md** | You are here! | 2 min |
| **README.md** | Project overview | 5 min |
| **QUICK_START.md** | Fast setup | 5 min |
| **SETUP_GUIDE.md** | Detailed setup | 15 min |
| **GETTING_GOOGLE_CREDENTIALS.md** | API keys | 10 min |
| **GOOGLE_DRIVE_SETUP.md** | Drive setup | 15 min |
| **API_DOCUMENTATION.md** | API reference | Reference |
| **PROJECT_OVERVIEW.md** | Architecture | 10 min |
| **WORKFLOW_DIAGRAM.md** | Visual flows | 5 min |
| **SAMPLE_CREDENTIALS.md** | Test accounts | 2 min |
| **CHECKLIST.md** | Setup checklist | Reference |

## 🎨 Features Highlights

### For Users
- 🎯 Comprehensive website analysis
- 🤖 AI-powered insights
- 💬 Interactive AI chat
- 📊 Visual charts and graphs
- 📄 Professional PDF reports
- 📈 Personal dashboard

### For Developers
- ⚡ FastAPI (async)
- 🗄️ MongoDB (NoSQL)
- 🔄 Redis (caching)
- 🎨 Tailwind CSS
- 🔐 JWT authentication
- 🐳 Docker ready
- 📝 Full API docs

## 🚀 Deployment Options

### Local Development
```bash
uvicorn app.main:app --reload
```

### Docker
```bash
docker-compose up --build
```

### Production
See [SETUP_GUIDE.md](SETUP_GUIDE.md) for production deployment.

## 💡 Tips

1. **Start Simple**: Get it running locally first
2. **Use Test Accounts**: Don't create real accounts yet
3. **Check Logs**: Terminal shows helpful error messages
4. **Read Docs**: We have comprehensive guides
5. **Ask Questions**: Open GitHub issues if stuck

## 🎯 Your Next Steps

1. ✅ Read this file (you're doing it!)
2. ✅ Follow [QUICK_START.md](QUICK_START.md)
3. ✅ Get your Gemini API key
4. ✅ Run the application
5. ✅ Test with sample accounts
6. ✅ Customize for your needs
7. ✅ Deploy to production

## 🤝 Need Help?

1. **Check documentation** - We have 10+ guides
2. **Review error messages** - They're usually helpful
3. **Check logs** - Terminal output shows issues
4. **GitHub Issues** - Open an issue
5. **Email** - support@websiteanalyzer.com

## 🎉 Success Checklist

You're ready when:
- ✅ Application starts without errors
- ✅ Can access http://localhost:8000
- ✅ Can login with test account
- ✅ Can analyze a website
- ✅ Results display correctly
- ✅ AI chat works

## 📞 Support

- **Documentation**: All .md files in root
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: support@websiteanalyzer.com

---

## 🎊 Ready to Start?

Choose your path:

**→ Quick Start (5 min)**: [QUICK_START.md](QUICK_START.md)

**→ Detailed Setup (15 min)**: [SETUP_GUIDE.md](SETUP_GUIDE.md)

**→ Get API Keys**: [GETTING_GOOGLE_CREDENTIALS.md](GETTING_GOOGLE_CREDENTIALS.md)

---

**Welcome aboard! Let's build something amazing! 🚀**
