from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisDetail, ChatRequest, ChatResponse
from app.core.security import get_current_user
from app.core.database import get_database
from app.services.analysis_service import perform_website_analysis
from app.services.ai_service import AIService
from app.utils.rate_limiter import check_rate_limit

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Create a new website analysis"""
    db = get_database()
    
    # Check rate limit
    user_id = current_user.get("user_id") if current_user else None
    plan = current_user.get("plan", "free") if current_user else "free"
    
    try:
        await check_rate_limit(user_id, plan, db)
    except HTTPException as e:
        raise e
    
    # Create analysis record
    analysis_dict = {
        "user_id": user_id,
        "website_url": str(analysis_data.website_url),
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = await db.analyses.insert_one(analysis_dict)
    analysis_id = str(result.inserted_id)
    
    # Run analysis immediately (not in background for now)
    # This ensures it completes without needing Celery
    try:
        print(f"🔍 Starting analysis for {analysis_data.website_url}")
        await perform_website_analysis(analysis_id, str(analysis_data.website_url))
        print(f"✅ Analysis completed for {analysis_id}")
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        import traceback
        traceback.print_exc()
        # Update status to failed
        await db.analyses.update_one(
            {"_id": ObjectId(analysis_id)},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
    
    return AnalysisResponse(
        id=analysis_id,
        website_url=str(analysis_data.website_url),
        status="processing",
        overall_score=None,
        created_at=analysis_dict["created_at"],
        completed_at=None
    )


@router.get("/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(analysis_id: str):
    """Get analysis details"""
    db = get_database()
    
    try:
        analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID"
        )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return AnalysisDetail(
        id=str(analysis["_id"]),
        website_url=analysis["website_url"],
        status=analysis["status"],
        overall_score=analysis.get("overall_score"),
        ux_analysis=analysis.get("ux_analysis"),
        seo_analysis=analysis.get("seo_analysis"),
        performance_analysis=analysis.get("performance_analysis"),
        content_analysis=analysis.get("content_analysis"),
        ai_summary=analysis.get("ai_summary"),
        priority_recommendations=analysis.get("priority_recommendations"),
        action_plan=analysis.get("action_plan"),
        screenshot_url=analysis.get("screenshot_url"),
        pdf_url=analysis.get("pdf_url"),
        created_at=analysis["created_at"],
        completed_at=analysis.get("completed_at")
    )


@router.post("/{analysis_id}/chat", response_model=ChatResponse)
async def chat_about_analysis(
    analysis_id: str,
    chat_request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Ask questions about the analysis"""
    db = get_database()
    
    # Get analysis
    try:
        analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID"
        )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    if analysis["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not completed yet"
        )
    
    # Get chat history
    chat_history = await db.chat_messages.find(
        {"analysis_id": analysis_id}
    ).sort("created_at", 1).to_list(length=50)
    
    # Generate AI response
    ai_service = AIService()
    response = await ai_service.chat_about_analysis(
        analysis,
        chat_request.message,
        chat_history
    )
    
    # Save messages
    user_message = {
        "analysis_id": analysis_id,
        "user_id": current_user.get("user_id") if current_user else None,
        "role": "user",
        "message": chat_request.message,
        "created_at": datetime.utcnow()
    }
    
    assistant_message = {
        "analysis_id": analysis_id,
        "user_id": current_user.get("user_id") if current_user else None,
        "role": "assistant",
        "message": response,
        "created_at": datetime.utcnow()
    }
    
    await db.chat_messages.insert_one(user_message)
    await db.chat_messages.insert_one(assistant_message)
    
    return ChatResponse(
        role="assistant",
        message=response,
        created_at=assistant_message["created_at"]
    )


@router.get("/{analysis_id}/pdf")
async def download_pdf(analysis_id: str):
    """Download PDF report"""
    db = get_database()
    
    try:
        analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    except Exception as e:
        print(f"❌ Error finding analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID"
        )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Check if analysis is complete
    if analysis.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis is {analysis.get('status', 'pending')}. Please wait for completion."
        )
    
    # Check if PDF exists
    pdf_url = analysis.get("pdf_url")
    if not pdf_url:
        # Try to generate PDF if it doesn't exist
        print(f"📄 PDF not found for analysis {analysis_id}, attempting to generate...")
        try:
            from app.services.pdf_service import PDFService
            pdf_service = PDFService()
            
            # Prepare data for PDF
            pdf_data = {
                'id': analysis_id,
                'website_url': analysis.get('website_url'),
                'overall_score': analysis.get('overall_score', 0),
                'ux_analysis': analysis.get('ux_analysis', {}),
                'seo_analysis': analysis.get('seo_analysis', {}),
                'performance_analysis': analysis.get('performance_analysis', {}),
                'content_analysis': analysis.get('content_analysis', {}),
                'ai_summary': analysis.get('ai_summary', 'No summary available'),
                'priority_recommendations': analysis.get('priority_recommendations', [])
            }
            
            # Generate PDF
            pdf_path = await pdf_service.generate_report(pdf_data)
            pdf_filename = f"analysis_{analysis_id}.pdf"
            pdf_url = f"/static/pdfs/{pdf_filename}"
            
            # Update database with PDF URL
            await db.analyses.update_one(
                {"_id": ObjectId(analysis_id)},
                {"$set": {"pdf_url": pdf_url}}
            )
            
            print(f"✅ PDF generated successfully: {pdf_url}")
            
        except Exception as e:
            print(f"❌ Failed to generate PDF: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF report"
            )
    
    # Verify PDF file exists
    import os
    pdf_file_path = f"app{pdf_url}"
    if not os.path.exists(pdf_file_path):
        print(f"⚠️ PDF file not found at: {pdf_file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on server"
        )
    
    print(f"✅ Returning PDF URL: {pdf_url}")
    return {"pdf_url": pdf_url, "status": "ready"}
