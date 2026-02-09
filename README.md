# 🚀 AI Website Analyzer for Business Growth

A professional, production-ready AI-powered tool that analyzes website UX, SEO, performance, and content to provide actionable growth recommendations.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

## 🚀 Features

- **Comprehensive Website Analysis**: UX/UI, SEO, Performance, Content Quality, Conversion Optimization
- **AI-Powered Insights**: Powered by Google Gemini 2.0 Flash
- **Interactive Q&A**: Ask questions about your analysis results
- **Professional PDF Reports**: Beautifully styled analysis documents
- **Personalized Dashboard**: Track multiple analyses and improvements over time
- **Visual Analytics**: Charts and graphs for better understanding
- **Freemium Model**: 1 free analysis for guests, unlimited for registered users
- **Multi-tier Plans**: Free, Basic, Pro, and Enterprise options

## 🛠️ Tech Stack

### Backend
- FastAPI (Python 3.11+)
- LangChain + Google Gemini API
- MongoDB Atlas
- Redis (Caching & Rate Limiting)
- Celery (Background Tasks)
- JWT Authentication

### Frontend
- Jinja2 Templates
- Tailwind CSS
- Vanilla JavaScript
- Chart.js (Visualizations)
- GSAP/Anime.js (Animations)

### DevOps
- Docker & Docker Compose
- Nginx (Production)
- Gunicorn/Uvicorn

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- MongoDB Atlas account
- Redis
- Google Gemini API key
- Google Drive API credentials (optional)

## ⚡ Quick Start (5 Minutes)

```bash
# 1. Clone and setup
git clone <repository-url>
cd ai-website-analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure (see GETTING_GOOGLE_CREDENTIALS.md)
cp .env.example .env
# Edit .env: Add MongoDB URL and Gemini API key

# 3. Seed test users
python scripts/seed_users.py

# 4. Run
uvicorn app.main:app --reload

# 5. Open http://localhost:8000
```

**Login with:** `basic@example.com` / `Basic@123`

📖 **Detailed Setup:** See [QUICK_START.md](QUICK_START.md) or [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🔧 Full Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd ai-website-analyzer
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 5. Run with Docker (Recommended)
```bash
docker-compose up --build
```

### 6. Run locally (Development)
```bash
# Start Redis
redis-server

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Access the Application

- **Landing Page**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Login**: http://localhost:8000/login
- **Analyze**: http://localhost:8000/analyze
- **Dashboard**: http://localhost:8000/dashboard

## 👥 Sample Login Credentials

### Free Plan (Guest)
- No login required - 1 analysis per session

### Basic Plan
- **Email**: basic@example.com
- **Password**: Basic@123
- **Limit**: 10 analyses/month

### Pro Plan
- **Email**: pro@example.com
- **Password**: Pro@123
- **Limit**: 100 analyses/month

### Enterprise Plan
- **Email**: enterprise@example.com
- **Password**: Enterprise@123
- **Limit**: Unlimited analyses

## 📁 Project Structure

```
ai-website-analyzer/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── analysis.py
│   │       │   ├── dashboard.py
│   │       │   └── users.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   └── celery_app.py
│   ├── models/
│   │   ├── user.py
│   │   ├── analysis.py
│   │   └── subscription.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── analysis_service.py
│   │   ├── pdf_service.py
│   │   └── storage_service.py
│   ├── analyzers/
│   │   ├── ux_analyzer.py
│   │   ├── seo_analyzer.py
│   │   ├── performance_analyzer.py
│   │   └── content_analyzer.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── analysis.py
│   │   └── auth.py
│   ├── templates/
│   │   ├── components/
│   │   ├── pages/
│   │   └── pdf/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── utils/
│   │   ├── helpers.py
│   │   └── validators.py
│   └── main.py
├── tests/
├── docker/
├── docs/
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🔑 Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `MONGODB_URL`: MongoDB Atlas connection string
- `GOOGLE_API_KEY`: Google Gemini API key
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT signing key
- `REDIS_URL`: Redis connection URL

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Analysis
- `POST /api/v1/analysis/analyze` - Start website analysis
- `GET /api/v1/analysis/{analysis_id}` - Get analysis results
- `POST /api/v1/analysis/{analysis_id}/chat` - Ask questions about analysis
- `GET /api/v1/analysis/{analysis_id}/pdf` - Download PDF report

### Dashboard
- `GET /api/v1/dashboard` - User dashboard
- `GET /api/v1/dashboard/analyses` - List user analyses
- `GET /api/v1/dashboard/stats` - User statistics

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_analysis.py
```

## 🚢 Deployment

### Docker Production Build
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
1. Set `ENVIRONMENT=production` in `.env`
2. Set `DEBUG=False`
3. Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
4. Configure proper CORS origins
5. Set up SSL certificates

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please read CONTRIBUTING.md for details.

## 📧 Support

For support, email support@websiteanalyzer.com or open an issue.

## 🎯 Roadmap

- [ ] Multi-page analysis
- [ ] Competitor comparison
- [ ] Historical tracking
- [ ] Browser extension
- [ ] API access for Pro users
- [ ] Team collaboration features
- [ ] White-label solution for Enterprise
- [ ] Scheduled re-analysis
- [ ] Webhook notifications
- [ ] A/B testing suggestions

## 📚 Complete Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[GETTING_GOOGLE_CREDENTIALS.md](GETTING_GOOGLE_CREDENTIALS.md)** - How to get API keys
- **[GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)** - Google Drive configuration
- **[SAMPLE_CREDENTIALS.md](SAMPLE_CREDENTIALS.md)** - Test account credentials
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Complete project overview
- **[WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md)** - Architecture diagrams

## 🎓 Key Features Explained

### For Users
- **Freemium Model**: Try for free, upgrade for more
- **AI-Powered**: Google Gemini 2.0 Flash for intelligent insights
- **Comprehensive**: UX, SEO, Performance, Content analysis
- **Interactive**: Chat with AI about your results
- **Professional**: Beautiful PDF reports
- **Dashboard**: Track all your analyses

### For Developers
- **Modern Stack**: FastAPI, MongoDB, Redis, Celery
- **Async**: Full async/await implementation
- **Scalable**: Background task processing
- **Secure**: JWT auth, rate limiting, input validation
- **Documented**: Complete API docs with Swagger
- **Tested**: Test suite included
- **Dockerized**: Easy deployment

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing web framework
- [Google Gemini](https://ai.google.dev/) - Powerful AI capabilities
- [Tailwind CSS](https://tailwindcss.com/) - Beautiful styling
- [GSAP](https://greensock.com/gsap/) - Smooth animations
- [MongoDB](https://www.mongodb.com/) - Flexible database
- [Redis](https://redis.io/) - Fast caching

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-website-analyzer/issues)
- **Email**: support@websiteanalyzer.com
- **Documentation**: See all .md files in root directory

## 📊 Project Stats

- **Lines of Code**: ~5,000+
- **Files**: 50+
- **Documentation**: 10+ comprehensive guides
- **Test Coverage**: Core features covered
- **Status**: Production Ready ✅

---

**Built with ❤️ for developers and businesses**

**Version**: 1.0.0 | **Last Updated**: February 2026 | **Status**: Production Ready ✅
