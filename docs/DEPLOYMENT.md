# Deployment Guide

Complete guide for deploying the AI Website Analyzer application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services
1. **MongoDB Atlas** (Free tier available)
   - Sign up at https://cloud.mongodb.com/
   - Create a cluster and get connection string
   - Whitelist your IP or use 0.0.0.0/0 for development

2. **Google Gemini API** (Free tier available)
   - Get API key from https://makersuite.google.com/app/apikey
   - Free tier: 60 requests per minute

3. **Redis** (Optional for local, required for production)
   - Local: Install via package manager
   - Production: Use managed service (Redis Cloud, AWS ElastiCache, etc.)

### Optional Services
4. **Google Drive API** (for cloud PDF storage)
   - Create service account at https://console.cloud.google.com/
   - Download `service-account-key.json`
   - Share Drive folder with service account email

---

## Local Development

### Method 1: Direct Python (Recommended for Development)

1. **Clone and Setup**
```bash
git clone <repository-url>
cd ai-website-analyzer
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Start Redis (if not using Docker)**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Windows
# Download from https://redis.io/download
```

6. **Run Application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access Application**
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

---

### Method 2: Docker Compose (Recommended for Testing)

1. **Prerequisites**
```bash
# Install Docker and Docker Compose
# https://docs.docker.com/get-docker/
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
# Important: Set REDIS_HOST=redis for Docker
```

3. **Build and Run**
```bash
# Development mode (with hot reload)
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web
```

4. **Stop Services**
```bash
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

---

## Docker Deployment

### Development Environment
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart web

# Stop all services
docker-compose down
```

### Production Environment
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale workers (if using Celery)
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f web

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Production Deployment

### Option 1: VPS/Cloud Server (DigitalOcean, AWS EC2, etc.)

1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Deploy Application**
```bash
# Clone repository
git clone <repository-url>
cd ai-website-analyzer

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Important production settings in .env:
# ENVIRONMENT=production
# DEBUG=False
# REDIS_HOST=redis
# Set strong SECRET_KEY and JWT_SECRET_KEY
```

3. **Start Services**
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d --build

# Check health
curl http://localhost:8000/api/v1/health
```

4. **Setup Nginx (Recommended)**
```bash
sudo apt install nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/website-analyzer
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /static {
        alias /path/to/ai-website-analyzer/app/static;
        expires 30d;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/website-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

### Option 2: Platform as a Service (Heroku, Railway, Render)

#### Railway.app (Recommended)
1. Connect GitHub repository
2. Add environment variables from `.env.example`
3. Railway auto-detects Dockerfile
4. Add Redis service from Railway marketplace
5. Deploy automatically on git push

#### Render.com
1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt && playwright install chromium`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Redis service
6. Configure environment variables

---

## Environment Variables

### Required Variables
```bash
# MongoDB (REQUIRED)
MONGODB_URL="mongodb+srv://user:pass@cluster.mongodb.net/"
MONGODB_DB_NAME="website_analyzer"

# Google Gemini API (REQUIRED)
GOOGLE_API_KEY="your-api-key"

# Security (REQUIRED)
SECRET_KEY="generate-strong-random-string"
JWT_SECRET_KEY="generate-strong-random-string"

# Redis (REQUIRED for production)
REDIS_URL="redis://redis:6379/0"
```

### Optional Variables
```bash
# Google Drive (for cloud PDF storage)
GOOGLE_DRIVE_CREDENTIALS_FILE="service-account-key.json"
GOOGLE_DRIVE_FOLDER_ID="folder-id"

# Email notifications
SMTP_HOST="smtp.gmail.com"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="app-password"
```

### Generate Secure Keys
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

---

## Troubleshooting

### Common Issues

**1. MongoDB Connection Failed**
```bash
# Check connection string format
# Ensure IP is whitelisted in MongoDB Atlas
# Test connection:
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/"
```

**2. Redis Connection Failed**
```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

**3. Playwright/Chromium Issues**
```bash
# Reinstall Playwright browsers
docker-compose exec web playwright install chromium
docker-compose exec web playwright install-deps chromium
```

**4. Permission Denied Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 app/static
```

**5. Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/api/v1/health

# Check Redis
docker-compose exec redis redis-cli ping

# Check logs
docker-compose logs -f web

# Check container status
docker-compose ps
```

### Performance Optimization

**1. Increase Workers (Production)**
```yaml
# In docker-compose.prod.yml
command: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**2. Redis Memory Optimization**
```yaml
# In docker-compose.prod.yml
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

**3. Enable Celery for Background Tasks**
```bash
# Uncomment celery_worker in docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d celery_worker
```

---

## Monitoring

### Application Logs
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web
```

### Resource Usage
```bash
# Check container stats
docker stats

# Check disk usage
docker system df
```

### Backup

**MongoDB Backup**
```bash
# Export database
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/website_analyzer" --out=backup/

# Import database
mongorestore --uri="mongodb+srv://user:pass@cluster.mongodb.net/website_analyzer" backup/website_analyzer/
```

**Redis Backup**
```bash
# Redis automatically saves to /data with AOF enabled
docker-compose exec redis redis-cli BGSAVE
```

---

## Scaling

### Horizontal Scaling
```bash
# Scale web service
docker-compose -f docker-compose.prod.yml up -d --scale web=3

# Use load balancer (Nginx, HAProxy, etc.)
```

### Vertical Scaling
```yaml
# Increase resources in docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
```

---

## Support

For issues and questions:
- Check documentation in `/docs` folder
- Review troubleshooting section above
- Check application logs
- Verify environment variables

---

**Last Updated:** February 2026
**Version:** 2.0.0
