# 🎯 Demo Commands - Quick Reference

## Before Demo

```bash
# 1. Start server
uvicorn app.main:app --reload

# 2. Verify MongoDB
python check_mongodb.py

# 3. Test all features
python test_features_integration.py

# 4. Open browser
# http://localhost:8000
```

## Test Credentials

```
Email: basic@example.com
Password: Basic@123
```

## Demo URLs

```
Landing:    http://localhost:8000
Login:      http://localhost:8000/login
Dashboard:  http://localhost:8000/dashboard
Analyze:    http://localhost:8000/analyze
API Docs:   http://localhost:8000/docs
```

## Demo Flow

### 1. Landing Page (30s)
- Show hero section
- Scroll to features
- Show pricing (₹499, ₹1,999, ₹4,999)

### 2. Guest Analysis (45s)
```
URL: https://example.com
```
- Enter URL
- Click "Analyze Website"
- Wait for results (~30s)
- Show scores

### 3. Advanced Features (45s)

**Action Plan:**
- Click "30/60/90 Day Plan" button
- Show roadmap modal
- Highlight 30/60/90 sections

**Export:**
- Click "Export" dropdown
- Download JSON
- Show file downloaded

**Share:**
- Click "Share Analysis"
- Set expiry: 7 days
- Generate link
- Copy link
- Open in new incognito tab
- Show beautiful HTML page

**PDF:**
- Click "Download PDF"
- Show professional report

### 4. Login & Dashboard (30s)
```
Login: basic@example.com / Basic@123
```
- Show dashboard
- View analysis history
- Show usage stats

### 5. AI Chat (30s)
```
Question: "How can I improve my SEO?"
```
- Type question
- Show AI response
- Ask follow-up
- Show context retention

## Key Talking Points

### Problem
- Audits cost $2,000-$10,000
- Take 2-4 weeks
- Need technical expertise

### Solution
- AI analysis in 2 minutes
- ₹499-₹4,999/month
- No technical knowledge needed

### Unique Features
1. 30/60/90 Day Action Plans ⭐
2. 3 Export Formats ⭐
3. Beautiful Share Pages ⭐
4. AI Chat with Memory
5. Real-time Analysis
6. Professional Reports
7. Team Collaboration

### Market
- $50B opportunity
- 200M+ websites
- 71% have websites

### Technology
- Google Gemini 1.5 Flash
- FastAPI + MongoDB
- Production-ready
- Scalable

## Troubleshooting

### Server won't start
```bash
# Check MongoDB
python check_mongodb.py

# Check .env file
cat .env | grep -E "MONGODB_URL|GOOGLE_API_KEY"
```

### Analysis stuck
```bash
# Check server logs
# Look for errors in terminal
```

### Share page shows JSON
```bash
# Restart server
# Clear browser cache
# Use incognito mode
```

## Quick Fixes

### Reset test user
```bash
python scripts/seed_users.py
```

### Check all features
```bash
python test_features_integration.py
```

### View MongoDB data
```bash
python check_mongodb.py
```

## Impressive Stats

- 70+ files created
- 6,000+ lines of code
- 20+ documentation files
- 5 advanced features
- 7 unique advantages
- $50B market
- Production-ready

## Competitive Advantages

| Feature | Us | Competitors |
|---------|----|-----------| 
| AI Analysis | ✅ | ❌ |
| Action Plans | ✅ | ❌ |
| Share Pages | ✅ | ❌ |
| Export Formats | 3 | 1 |
| AI Chat | ✅ | ❌ |
| Price | ₹499 | ₹5,000+ |
| Time | 2 min | 2-4 weeks |

## Revenue Projections

- Year 1: ₹2.5 Cr ARR
- Year 2: ₹20 Cr ARR
- Year 3: ₹140 Cr ARR

## Closing Statement

"We've built a production-ready AI Website Analyzer that makes professional website audits accessible to everyone. With 7 unique features, modern technology, and a clear path to revenue, we're ready to capture a significant share of the $50 billion market."

---

**Good luck! 🚀**
