from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, List
from datetime import datetime


class AnalysisCreate(BaseModel):
    website_url: HttpUrl


class AnalysisResponse(BaseModel):
    id: str
    website_url: str
    status: str
    overall_score: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]


class AnalysisDetail(BaseModel):
    id: str
    website_url: str
    status: str
    overall_score: Optional[float]
    ux_analysis: Optional[Dict]
    seo_analysis: Optional[Dict]
    performance_analysis: Optional[Dict]
    content_analysis: Optional[Dict]
    ai_summary: Optional[str]
    priority_recommendations: Optional[List[Dict]]
    screenshot_url: Optional[str]
    pdf_url: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    role: str
    message: str
    created_at: datetime
