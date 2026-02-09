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
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService


async def perform_website_analysis(analysis_id: str, website_url: str):
    """Perform complete website analysis"""
    db = get_database()
    
    try:
        print(f"📊 Analysis {analysis_id}: Starting for {website_url}")
        
        # Update status to processing
        await db.analyses.update_one(
            {"_id": ObjectId(analysis_id)},
            {"$set": {"status": "processing"}}
        )
        print(f"📊 Analysis {analysis_id}: Status updated to processing")
        
        # Initialize analyzers
        print(f"📊 Analysis {analysis_id}: Initializing analyzers...")
        ux_analyzer = UXAnalyzer()
        seo_analyzer = SEOAnalyzer()
        performance_analyzer = PerformanceAnalyzer()
        content_analyzer = ContentAnalyzer()
        ai_service = AIService()
        
        # Run analyses in parallel
        print(f"📊 Analysis {analysis_id}: Running analyzers...")
        ux_result, seo_result, perf_result, content_result = await asyncio.gather(
            ux_analyzer.analyze(website_url),
            seo_analyzer.analyze(website_url),
            performance_analyzer.analyze(website_url),
            content_analyzer.analyze(website_url),
            return_exceptions=True
        )
        print(f"📊 Analysis {analysis_id}: Analyzers completed")
        
        # Handle any errors
        if isinstance(ux_result, Exception):
            print(f"⚠️  UX analyzer error: {ux_result}")
            ux_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        if isinstance(seo_result, Exception):
            print(f"⚠️  SEO analyzer error: {seo_result}")
            seo_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        if isinstance(perf_result, Exception):
            print(f"⚠️  Performance analyzer error: {perf_result}")
            perf_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        if isinstance(content_result, Exception):
            print(f"⚠️  Content analyzer error: {content_result}")
            content_result = {"score": 0, "issues": ["Analysis failed"], "recommendations": []}
        
        # Calculate overall score
        overall_score = (
            ux_result.get("score", 0) * 0.25 +
            seo_result.get("score", 0) * 0.25 +
            perf_result.get("score", 0) * 0.25 +
            content_result.get("score", 0) * 0.25
        )
        print(f"📊 Analysis {analysis_id}: Overall score calculated: {overall_score}")
        
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
        print(f"📊 Analysis {analysis_id}: Generating AI insights...")
        ai_summary = await ai_service.generate_analysis_summary(analysis_data)
        priority_recommendations = await ai_service.generate_priority_recommendations(analysis_data)
        print(f"📊 Analysis {analysis_id}: AI insights generated")
        
        # Generate action plan
        print(f"📊 Analysis {analysis_id}: Generating action plan...")
        action_plan = await ai_service.generate_action_plan(analysis_data)
        print(f"📊 Analysis {analysis_id}: Action plan generated")
        
        # Generate PDF report
        print(f"📊 Analysis {analysis_id}: Generating PDF report...")
        pdf_url = None
        try:
            pdf_service = PDFService()
            
            # Prepare data for PDF
            pdf_data = {
                'id': analysis_id,
                'website_url': website_url,
                'overall_score': round(overall_score, 2),
                'ux_analysis': ux_result,
                'seo_analysis': seo_result,
                'performance_analysis': perf_result,
                'content_analysis': content_result,
                'ai_summary': ai_summary,
                'priority_recommendations': priority_recommendations
            }
            
            # Generate PDF (saves directly to app/static/pdfs/)
            pdf_path = await pdf_service.generate_report(pdf_data)
            
            # PDF URL for accessing via web
            pdf_filename = f"analysis_{analysis_id}.pdf"
            pdf_url = f"/static/pdfs/{pdf_filename}"
            
            print(f"✅ PDF generated successfully: {pdf_url}")
            
        except Exception as pdf_error:
            print(f"⚠️  PDF generation error: {pdf_error}")
            import traceback
            traceback.print_exc()
        
        # Update analysis with results
        update_data = {
            "status": "completed",
            "overall_score": round(overall_score, 2),
            "ux_analysis": ux_result,
            "seo_analysis": seo_result,
            "performance_analysis": perf_result,
            "content_analysis": content_result,
            "ai_summary": ai_summary,
            "priority_recommendations": priority_recommendations,
            "action_plan": action_plan,
            "completed_at": datetime.utcnow()
        }
        
        if pdf_url:
            update_data["pdf_url"] = pdf_url
        
        await db.analyses.update_one(
            {"_id": ObjectId(analysis_id)},
            {"$set": update_data}
        )
        print(f"✅ Analysis {analysis_id}: Completed successfully!")
        
    except Exception as e:
        print(f"❌ Analysis {analysis_id}: Failed with error: {e}")
        import traceback
        traceback.print_exc()
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
