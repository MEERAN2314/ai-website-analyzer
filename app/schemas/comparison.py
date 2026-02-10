from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class ComparisonCreateRequest(BaseModel):
    """Request to create a new comparison"""
    your_url: HttpUrl
    competitor_urls: List[HttpUrl]
    
    class Config:
        json_schema_extra = {
            "example": {
                "your_url": "https://example.com",
                "competitor_urls": [
                    "https://competitor1.com",
                    "https://competitor2.com"
                ]
            }
        }


class ComparisonResponse(BaseModel):
    """Response after creating comparison"""
    comparison_id: str
    status: str
    message: str


class CompetitorResult(BaseModel):
    """Individual competitor results"""
    url: str
    overall_score: float
    ux_score: float
    seo_score: float
    performance_score: float
    content_score: float
    security_score: float
    image_score: float
    rank: int


class CategoryRanking(BaseModel):
    """Ranking for a specific category"""
    url: str
    score: float
    rank: int
    medal: Optional[str] = None  # 🥇🥈🥉


class ComparisonDetail(BaseModel):
    """Detailed comparison results"""
    id: str
    your_website: CompetitorResult
    competitors: List[CompetitorResult]
    rankings: Dict[str, List[CategoryRanking]]
    strengths: List[Dict]
    weaknesses: List[Dict]
    opportunities: List[Dict]
    ai_insights: Optional[str] = None
    pdf_url: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
