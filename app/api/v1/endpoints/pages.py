from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request):
    """Analysis page"""
    return templates.TemplateResponse("pages/analyze.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("pages/dashboard.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("pages/login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse("pages/register.html", {"request": request})


@router.get("/results/{analysis_id}", response_class=HTMLResponse)
async def results_page(request: Request, analysis_id: str):
    """Results page"""
    return templates.TemplateResponse(
        "pages/results.html",
        {"request": request, "analysis_id": analysis_id}
    )


@router.get("/compare", response_class=HTMLResponse)
async def comparison_create_page(request: Request):
    """Competitor comparison creation page"""
    return templates.TemplateResponse("pages/comparison_create.html", {"request": request})


@router.get("/comparison/{comparison_id}", response_class=HTMLResponse)
async def comparison_results_page(request: Request, comparison_id: str):
    """Comparison results page"""
    return templates.TemplateResponse(
        "pages/comparison_results.html",
        {"request": request, "comparison_id": comparison_id}
    )


@router.get("/share/comparison/{share_token}", response_class=HTMLResponse)
async def shared_comparison_page(request: Request, share_token: str):
    """Shared comparison page"""
    return templates.TemplateResponse(
        "pages/shared_comparison.html",
        {"request": request, "share_token": share_token}
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page"""
    return templates.TemplateResponse("pages/profile.html", {"request": request})


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """User settings page"""
    return templates.TemplateResponse("pages/profile.html", {"request": request})
