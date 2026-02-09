from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

from app.core.config import settings
from app.core.database import get_database
from app.analyzers.ux_analyzer import UXAnalyzer
from app.analyzers.seo_analyzer import SEOAnalyzer
from app.analyzers.performance_analyzer import PerformanceAnalyzer
from app.analyzers.content_analyzer import ContentAnalyzer
from app.services.ai_service import AIService


async def perform_website_analysis(analysis_id: str, website_url: str):
    """Perform complete website analysis"""
    db = get_database()
    
    try:
        # Update status to processing
        await db.analyses.update_one(
            {"_id": ObjectId(analysis_id)},
            {"$set": {"status": "processing"}}
        )
        
        # Initialize analyzers
        ux_analyzer = UXAnalyzer()
        seo_analyzer = SEOAnalyzer()
        performance_analyzer = PerformanceAnalyzer()
        content_analyzer = ContentAnalyzer()
        ai_service = AIService()
        
        # Run analyses in parallel
        ux_result, seo_result, perf_result, content_result = await asyncio.gather(
            ux_analyzer.analyze(website_url),
            seo_analyzer.analyze(website_url),
            performance_analyzer.analyze(website_url),
            content_analyzer.analyze(website_url),
            return_exceptions=True
        )
        
        # Handle any errors
        if isinstance(ux_result, Exception):
            ux_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        if isinstance(seo_result, Exception):
            seo_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        if isinstance(perf_result, Exception):
            perf_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        if isinstance(content_result, Exception):
            content_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        
        # Calculate overall score
        overall_score = (
            ux_result.get("score", 0) * 0.25 +
            seo_result.get("score", 0) * 0.25 +
            perf_result.get("score", 0) * 0.25 +
            content_result.get("score", 0) * 0.25
        )
        
        # Prepare analysis data for AI
        analysis_data = {
            "website_url": website_url,
            "overall_score": overall_score,
            "ux_analysis": ux_result,
            "seo_analysis": seo_result,
            "performance_analysis": perf_result,
            "content_analysis": content_result
        }
        
        # Generate AI insights
        ai_summary = await ai_service.generate_analysis_summary(analysis_data)
        priority_recommendations = await ai_service.generate_priority_recommendations(analysis_data)
        
        # Update analysis with results
        await db.analyses.update_one(
            {"_id": ObjectId(analysis_id)},
            {
                "$set": {
                    "status": "completed",
                    "overall_score": round(overall_score, 2),
                    "ux_analysis": ux_result,
                    "seo_analysis": seo_result,
                    "performance_analysis": perf_result,
                    "content_analysis": content_result,
                    "ai_summary": ai_summary,
                    "priority_recommendations": priority_recommendations,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
    except Exception as e:
        # Update status to failed
        await db.analyses.update_one(
            {"_id": ObjectId(analysis_id)},
            {
                "$set": {
                    "status": "failed",
                    "error_message": str(e),
                    "completed_at": datetime.utcnow()
                }
            }
        )
