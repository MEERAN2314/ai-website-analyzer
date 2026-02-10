from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.v1.router import api_router

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered website analyzer for business growth",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Database events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Root route - Landing page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("pages/landing.html", {"request": request})

# Page routes (not under /api/v1)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("pages/register.html", {"request": request})

@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    return templates.TemplateResponse("pages/analyze.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})

@app.get("/results/{analysis_id}", response_class=HTMLResponse)
async def results_page(request: Request, analysis_id: str):
    return templates.TemplateResponse(
        "pages/results.html",
        {"request": request, "analysis_id": analysis_id}
    )

@app.get("/compare", response_class=HTMLResponse)
async def comparison_create_page(request: Request):
    """Competitor comparison creation page"""
    return templates.TemplateResponse("pages/comparison_create.html", {"request": request})

@app.get("/comparison/{comparison_id}", response_class=HTMLResponse)
async def comparison_results_page(request: Request, comparison_id: str):
    """Comparison results page"""
    return templates.TemplateResponse(
        "pages/comparison_results.html",
        {"request": request, "comparison_id": comparison_id}
    )

@app.get("/share/{share_token}", response_class=HTMLResponse)
async def shared_analysis_page(request: Request, share_token: str):
    """Render shared analysis page"""
    return templates.TemplateResponse(
        "pages/shared_analysis.html",
        {"request": request, "share_token": share_token}
    )

@app.get("/share/comparison/{share_token}", response_class=HTMLResponse)
async def shared_comparison_page(request: Request, share_token: str):
    """Shared comparison page"""
    return templates.TemplateResponse(
        "pages/shared_comparison.html",
        {"request": request, "share_token": share_token}
    )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page"""
    return templates.TemplateResponse("pages/profile.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """User settings page"""
    return templates.TemplateResponse("pages/profile.html", {"request": request})

@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    """Pricing page"""
    return templates.TemplateResponse("pages/pricing.html", {"request": request})

@app.get("/clear-session", response_class=HTMLResponse)
async def clear_session_page(request: Request):
    """Clear session and logout"""
    return templates.TemplateResponse("pages/clear_session.html", {"request": request})

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/api/v1/health")
async def api_health_check():
    """Comprehensive health check for monitoring"""
    import time
    from app.core.database import db
    from app.core.redis import redis_client
    
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "services": {}
    }
    
    # Check MongoDB
    try:
        await db.command("ping")
        health_status["services"]["mongodb"] = "healthy"
    except Exception as e:
        health_status["services"]["mongodb"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        await redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
