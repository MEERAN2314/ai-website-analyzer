# Application Workflow & Architecture

## User Journey Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         LANDING PAGE                             │
│  - Hero section with value proposition                           │
│  - How it works (3 steps)                                        │
│  - Features showcase                                             │
│  - Pricing plans                                                 │
│  - CTA: "Analyze Your Website"                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  User Decision  │
                    └─────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        ┌──────────────┐            ┌──────────────┐
        │ Guest User   │            │ Register/    │
        │ (No Login)   │            │ Login        │
        └──────────────┘            └──────────────┘
                │                           │
                │                           ▼
                │                   ┌──────────────┐
                │                   │ Dashboard    │
                │                   │ - Stats      │
                │                   │ - History    │
                │                   └──────────────┘
                │                           │
                └───────────┬───────────────┘
                            ▼
                    ┌──────────────┐
                    │ ANALYZE PAGE │
                    │ Enter URL    │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Rate Limit   │
                    │ Check        │
                    └──────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │ Limit OK     │        │ Limit        │
        │ Start        │        │ Exceeded     │
        │ Analysis     │        │ Show Error   │
        └──────────────┘        └──────────────┘
                │
                ▼
        ┌──────────────┐
        │ PROCESSING   │
        │ - UX         │
        │ - SEO        │
        │ - Performance│
        │ - Content    │
        │ - AI Summary │
        └──────────────┘
                │
                ▼
        ┌──────────────┐
        │ RESULTS PAGE │
        │ - Scores     │
        │ - Summary    │
        │ - Details    │
        │ - AI Chat    │
        │ - PDF Export │
        └──────────────┘
```

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
│  - HTML/CSS/JavaScript                                           │
│  - Tailwind CSS styling                                          │
│  - GSAP animations                                               │
│  - Chart.js visualizations                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Endpoints                         │   │
│  │  - /auth/*        (Authentication)                       │   │
│  │  - /analysis/*    (Website Analysis)                     │   │
│  │  - /dashboard/*   (User Dashboard)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Middleware Layer                        │   │
│  │  - CORS                                                  │   │
│  │  - Rate Limiting                                         │   │
│  │  - JWT Validation                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Business Logic                          │   │
│  │  - Authentication Service                                │   │
│  │  - Analysis Service                                      │   │
│  │  - AI Service (Gemini)                                   │   │
│  │  - PDF Service                                           │   │
│  │  - Storage Service (Drive)                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   MongoDB    │    │    Redis     │    │   Celery     │
│   Database   │    │   Cache      │    │   Worker     │
│              │    │              │    │              │
│ - Users      │    │ - Sessions   │    │ - Analysis   │
│ - Analyses   │    │ - Rate Limit │    │   Tasks      │
│ - Chat Msgs  │    │ - Temp Data  │    │ - PDF Gen    │
└──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                                ▼
                                    ┌──────────────────┐
                                    │  External APIs   │
                                    │                  │
                                    │ - Google Gemini  │
                                    │ - Google Drive   │
                                    └──────────────────┘
```

## Analysis Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Submits URL                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Create Analysis Record (status: pending)                     │
│     - Save to MongoDB                                            │
│     - Return analysis_id to user                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Queue Background Task (Celery)                               │
│     - Update status: processing                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Run Analyzers in Parallel                                    │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ UX Analyzer  │  │ SEO Analyzer │  │ Performance  │          │
│  │              │  │              │  │  Analyzer    │          │
│  │ - Fetch HTML │  │ - Parse meta │  │ - Measure    │          │
│  │ - Check      │  │ - Check tags │  │   load time  │          │
│  │   viewport   │  │ - Extract    │  │ - Count      │          │
│  │ - Validate   │  │   keywords   │  │   requests   │          │
│  │   images     │  │ - Verify SSL │  │ - Check size │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐                                                │
│  │   Content    │                                                │
│  │   Analyzer   │                                                │
│  │              │                                                │
│  │ - Count words│                                                │
│  │ - Check CTA  │                                                │
│  │ - Analyze    │                                                │
│  │   readability│                                                │
│  └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Calculate Overall Score                                      │
│     - UX Score × 25%                                             │
│     - SEO Score × 25%                                            │
│     - Performance Score × 25%                                    │
│     - Content Score × 25%                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Generate AI Insights (Google Gemini)                         │
│     - Send analysis data to Gemini                               │
│     - Get comprehensive summary                                  │
│     - Generate priority recommendations                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Generate PDF Report (Optional)                               │
│     - Create HTML template                                       │
│     - Convert to PDF with WeasyPrint                             │
│     - Upload to Google Drive                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. Update Analysis Record                                       │
│     - Status: completed                                          │
│     - Save all results to MongoDB                                │
│     - Set completed_at timestamp                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  8. User Views Results                                           │
│     - Display scores and charts                                  │
│     - Show AI summary                                            │
│     - Enable AI chat                                             │
│     - Provide PDF download                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      REGISTRATION                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    User submits form
                    (email, password, name)
                              │
                              ▼
                    Validate input
                    (Pydantic schema)
                              │
                              ▼
                    Check if email exists
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                  Exists            New User
                    │                   │
                    ▼                   ▼
              Return error      Hash password
                                (bcrypt)
                                      │
                                      ▼
                                Save to MongoDB
                                (plan: basic)
                                      │
                                      ▼
                                Return user data

┌─────────────────────────────────────────────────────────────────┐
│                         LOGIN                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    User submits credentials
                    (email, password)
                              │
                              ▼
                    Find user in MongoDB
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                Not Found           Found
                    │                   │
                    ▼                   ▼
              Return 401        Verify password
                                (bcrypt compare)
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                          Invalid         Valid
                              │               │
                              ▼               ▼
                        Return 401    Generate JWT tokens
                                      (access + refresh)
                                              │
                                              ▼
                                      Return tokens

┌─────────────────────────────────────────────────────────────────┐
│                    PROTECTED ROUTE ACCESS                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Request with token
                    (Authorization: Bearer <token>)
                              │
                              ▼
                    Extract token from header
                              │
                              ▼
                    Decode & verify JWT
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                Invalid             Valid
                    │                   │
                    ▼                   ▼
              Return 401        Extract user_id
                                      │
                                      ▼
                                Get user from DB
                                      │
                                      ▼
                                Allow access
```

## Rate Limiting Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              User Requests Analysis                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Check if authenticated
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                Guest                Registered
                    │                   │
                    ▼                   ▼
              Limit: 1          Get user plan
                                      │
                              ┌───────┼───────┐
                              ▼       ▼       ▼
                          Basic   Pro    Enterprise
                            │       │         │
                            ▼       ▼         ▼
                        Limit:10  100    Unlimited
                              │
                              ▼
                    Check monthly count
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              Under Limit         Over Limit
                    │                   │
                    ▼                   ▼
              Increment count     Return 429
              Allow analysis      (Too Many Requests)
```

## Data Models

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER MODEL                               │
├─────────────────────────────────────────────────────────────────┤
│ _id: ObjectId                                                    │
│ email: string (unique)                                           │
│ hashed_password: string                                          │
│ full_name: string                                                │
│ plan: enum (free, basic, pro, enterprise)                        │
│ is_active: boolean                                               │
│ is_verified: boolean                                             │
│ created_at: datetime                                             │
│ updated_at: datetime                                             │
│ analyses_count: integer                                          │
│ monthly_analyses_count: integer                                  │
│ monthly_reset_date: datetime                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      ANALYSIS MODEL                              │
├─────────────────────────────────────────────────────────────────┤
│ _id: ObjectId                                                    │
│ user_id: string (optional)                                       │
│ website_url: string                                              │
│ status: enum (pending, processing, completed, failed)            │
│ overall_score: float                                             │
│ ux_analysis: object                                              │
│   - score: float                                                 │
│   - issues: array                                                │
│   - recommendations: array                                       │
│   - mobile_friendly: boolean                                     │
│   - accessibility_score: float                                   │
│ seo_analysis: object                                             │
│ performance_analysis: object                                     │
│ content_analysis: object                                         │
│ ai_summary: string                                               │
│ priority_recommendations: array                                  │
│ screenshot_url: string                                           │
│ pdf_url: string                                                  │
│ error_message: string                                            │
│ created_at: datetime                                             │
│ completed_at: datetime                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CHAT MESSAGE MODEL                            │
├─────────────────────────────────────────────────────────────────┤
│ _id: ObjectId                                                    │
│ analysis_id: string                                              │
│ user_id: string (optional)                                       │
│ role: enum (user, assistant)                                     │
│ message: string                                                  │
│ created_at: datetime                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRODUCTION                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Load Balancer  │
                    │     (Nginx)      │
                    └──────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        ┌──────────────┐            ┌──────────────┐
        │  FastAPI     │            │  FastAPI     │
        │  Instance 1  │            │  Instance 2  │
        └──────────────┘            └──────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
                    ┌──────────────────┐
                    │  MongoDB Atlas   │
                    │   (Cluster)      │
                    └──────────────────┘
                              │
                    ┌──────────────────┐
                    │  Redis Cluster   │
                    │   (Caching)      │
                    └──────────────────┘
                              │
                    ┌──────────────────┐
                    │  Celery Workers  │
                    │  (Multiple)      │
                    └──────────────────┘
                              │
                    ┌──────────────────┐
                    │  Google Drive    │
                    │  (PDF Storage)   │
                    └──────────────────┘
```

---

This diagram shows the complete flow from user interaction to data storage and processing!
