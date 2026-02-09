from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, HttpUrl
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class AnalysisStatus(str):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UXAnalysis(BaseModel):
    score: float
    issues: List[str]
    recommendations: List[str]
    mobile_friendly: bool
    accessibility_score: float


class SEOAnalysis(BaseModel):
    score: float
    meta_title: Optional[str]
    meta_description: Optional[str]
    headings_structure: Dict
    keywords: List[str]
    issues: List[str]
    recommendations: List[str]


class PerformanceAnalysis(BaseModel):
    score: float
    load_time: float
    page_size: float
    requests_count: int
    core_web_vitals: Dict
    issues: List[str]
    recommendations: List[str]


class ContentAnalysis(BaseModel):
    score: float
    readability_score: float
    word_count: int
    has_cta: bool
    tone: str
    issues: List[str]
    recommendations: List[str]


class Analysis(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: Optional[str] = None
    website_url: HttpUrl
    status: str = AnalysisStatus.PENDING
    
    # Analysis results
    overall_score: Optional[float] = None
    ux_analysis: Optional[UXAnalysis] = None
    seo_analysis: Optional[SEOAnalysis] = None
    performance_analysis: Optional[PerformanceAnalysis] = None
    content_analysis: Optional[ContentAnalysis] = None
    
    # AI insights
    ai_summary: Optional[str] = None
    priority_recommendations: Optional[List[Dict]] = None
    
    # Metadata
    screenshot_url: Optional[str] = None
    pdf_url: Optional[str] = None
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatMessage(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    analysis_id: str
    user_id: Optional[str] = None
    role: str  # "user" or "assistant"
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
