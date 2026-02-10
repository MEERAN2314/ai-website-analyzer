from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class CompetitorData(BaseModel):
    """Individual competitor data"""
    url: str
    analysis_id: Optional[str] = None
    overall_score: float = 0
    ux_score: float = 0
    seo_score: float = 0
    performance_score: float = 0
    content_score: float = 0
    security_score: float = 0
    image_score: float = 0
    rank: int = 0
    analysis_data: Optional[Dict] = None


class ComparisonCreate(BaseModel):
    """Request to create a new comparison"""
    your_url: str
    competitor_urls: List[str]


class ComparisonRankings(BaseModel):
    """Rankings for each category"""
    overall: List[Dict]
    ux: List[Dict]
    seo: List[Dict]
    performance: List[Dict]
    content: List[Dict]
    security: List[Dict]
    images: List[Dict]


class ComparisonInsights(BaseModel):
    """Competitive insights"""
    strengths: List[Dict]
    weaknesses: List[Dict]
    opportunities: List[Dict]
    threats: List[Dict]


class ComparisonResponse(BaseModel):
    """Basic comparison response"""
    id: str
    your_website_url: str
    competitor_count: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class ComparisonDetail(BaseModel):
    """Detailed comparison results"""
    id: str
    user_id: Optional[str] = None
    your_website: CompetitorData
    competitors: List[CompetitorData]
    rankings: Optional[Dict] = None
    insights: Optional[Dict] = None
    ai_summary: Optional[str] = None
    pdf_url: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
