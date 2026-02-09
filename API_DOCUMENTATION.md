# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass@123",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "plan": "basic",
  "is_active": true,
  "created_at": "2026-02-09T10:00:00Z",
  "analyses_count": 0,
  "monthly_analyses_count": 0
}
```

### Login
**POST** `/auth/login`

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass@123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Refresh Token
**POST** `/auth/refresh`

Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## Analysis Endpoints

### Create Analysis
**POST** `/analysis/analyze`

Start a new website analysis.

**Authentication:** Optional (required for multiple analyses)

**Request Body:**
```json
{
  "website_url": "https://example.com"
}
```

**Response:** `200 OK`
```json
{
  "id": "analysis_id",
  "website_url": "https://example.com",
  "status": "pending",
  "overall_score": null,
  "created_at": "2026-02-09T10:00:00Z",
  "completed_at": null
}
```

### Get Analysis
**GET** `/analysis/{analysis_id}`

Retrieve analysis results.

**Response:** `200 OK`
```json
{
  "id": "analysis_id",
  "website_url": "https://example.com",
  "status": "completed",
  "overall_score": 85.5,
  "ux_analysis": {
    "score": 88,
    "issues": ["Missing alt text on images"],
    "recommendations": ["Add descriptive alt text"],
    "mobile_friendly": true,
    "accessibility_score": 85
  },
  "seo_analysis": {
    "score": 82,
    "meta_title": "Example Domain",
    "meta_description": "Example description",
    "headings_structure": {"h1": 1, "h2": 3, "h3": 5},
    "keywords": ["example", "domain"],
    "issues": ["Meta description too short"],
    "recommendations": ["Optimize meta description length"]
  },
  "performance_analysis": {
    "score": 78,
    "load_time": 2.5,
    "page_size": 450.5,
    "requests_count": 25,
    "core_web_vitals": {
      "LCP": 2500,
      "FID": 50,
      "CLS": 0.1
    },
    "issues": ["Large page size"],
    "recommendations": ["Compress images"]
  },
  "content_analysis": {
    "score": 90,
    "readability_score": 80,
    "word_count": 500,
    "has_cta": true,
    "tone": "Positive",
    "issues": [],
    "recommendations": ["Add more headings"]
  },
  "ai_summary": "Your website shows strong performance...",
  "priority_recommendations": [
    {
      "title": "Improve Page Load Speed",
      "description": "Optimize images and enable caching",
      "priority": "High",
      "impact": "High",
      "effort": "Medium",
      "category": "Performance"
    }
  ],
  "screenshot_url": null,
  "pdf_url": null,
  "created_at": "2026-02-09T10:00:00Z",
  "completed_at": "2026-02-09T10:02:30Z"
}
```

### Chat About Analysis
**POST** `/analysis/{analysis_id}/chat`

Ask questions about the analysis.

**Authentication:** Optional

**Request Body:**
```json
{
  "message": "How can I improve my SEO score?"
}
```

**Response:** `200 OK`
```json
{
  "role": "assistant",
  "message": "To improve your SEO score, focus on...",
  "created_at": "2026-02-09T10:05:00Z"
}
```

### Download PDF
**GET** `/analysis/{analysis_id}/pdf`

Get PDF report URL.

**Response:** `200 OK`
```json
{
  "pdf_url": "https://drive.google.com/file/d/..."
}
```

---

## Dashboard Endpoints

### Get Dashboard
**GET** `/dashboard/`

Get user dashboard data.

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "user": {
    "email": "user@example.com",
    "full_name": "John Doe",
    "plan": "pro",
    "analyses_count": 25,
    "monthly_analyses_count": 15
  },
  "stats": {
    "total_analyses": 25,
    "completed_analyses": 23,
    "average_score": 82.5
  },
  "recent_analyses": [
    {
      "id": "analysis_id",
      "website_url": "https://example.com",
      "status": "completed",
      "overall_score": 85.5,
      "created_at": "2026-02-09T10:00:00Z"
    }
  ]
}
```

### Get User Analyses
**GET** `/dashboard/analyses?skip=0&limit=20`

List all user analyses with pagination.

**Authentication:** Required

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Number of records to return (default: 20)

**Response:** `200 OK`
```json
[
  {
    "id": "analysis_id",
    "website_url": "https://example.com",
    "status": "completed",
    "overall_score": 85.5,
    "created_at": "2026-02-09T10:00:00Z",
    "completed_at": "2026-02-09T10:02:30Z"
  }
]
```

### Get User Stats
**GET** `/dashboard/stats`

Get detailed user statistics.

**Authentication:** Required

**Response:** `200 OK`
```json
{
  "status_counts": {
    "pending": 2,
    "processing": 1,
    "completed": 20,
    "failed": 2
  },
  "daily_analyses": [
    {"date": "2026-02-01", "count": 3},
    {"date": "2026-02-02", "count": 5}
  ],
  "score_distribution": [
    {"_id": 80, "count": 10},
    {"_id": 60, "count": 5}
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Monthly analysis limit reached. Upgrade your plan for more analyses."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limits

| Plan | Analyses/Month | API Requests/Day |
|------|----------------|------------------|
| Free | 1 | N/A |
| Basic | 10 | N/A |
| Pro | 100 | 100 |
| Enterprise | Unlimited | Unlimited |

---

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## Examples

### Complete Analysis Flow

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123","full_name":"Test User"}'

# 2. Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123"}' \
  | jq -r '.access_token')

# 3. Start Analysis
ANALYSIS_ID=$(curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"website_url":"https://example.com"}' \
  | jq -r '.id')

# 4. Check Results (wait a few seconds)
curl -X GET "http://localhost:8000/api/v1/analysis/$ANALYSIS_ID" \
  -H "Authorization: Bearer $TOKEN"

# 5. Ask Question
curl -X POST "http://localhost:8000/api/v1/analysis/$ANALYSIS_ID/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"How can I improve my score?"}'

# 6. View Dashboard
curl -X GET "http://localhost:8000/api/v1/dashboard/" \
  -H "Authorization: Bearer $TOKEN"
```

---

For interactive API documentation, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
