from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId

from app.schemas.comparison import (
    ComparisonCreateRequest,
    ComparisonResponse,
    ComparisonDetail
)
from app.services.comparison_service import ComparisonService
from app.core.database import get_database

router = APIRouter()


@router.post("/", response_model=ComparisonResponse)
async def create_comparison(request: ComparisonCreateRequest):
    """
    Create a new competitor comparison analysis
    
    - **your_url**: Your website URL
    - **competitor_urls**: List of competitor URLs (1-5)
    """
    
    # Validate competitor count
    if len(request.competitor_urls) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 competitor URL is required"
        )
    
    if len(request.competitor_urls) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 competitors allowed"
        )
    
    # Check for duplicate URLs
    all_urls = [str(request.your_url)] + [str(url) for url in request.competitor_urls]
    if len(all_urls) != len(set(all_urls)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate URLs detected. Each URL must be unique."
        )
    
    try:
        comparison_service = ComparisonService()
        comparison_id = await comparison_service.create_comparison(
            your_url=str(request.your_url),
            competitor_urls=[str(url) for url in request.competitor_urls]
        )
        
        return ComparisonResponse(
            comparison_id=comparison_id,
            status="processing",
            message=f"Comparison started. Analyzing {len(request.competitor_urls) + 1} websites..."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comparison: {str(e)}"
        )


@router.get("/{comparison_id}")
async def get_comparison(comparison_id: str):
    """
    Get comparison results by ID
    
    - **comparison_id**: The comparison ID
    """
    
    try:
        comparison_service = ComparisonService()
        comparison = await comparison_service.get_comparison(comparison_id)
        
        if not comparison:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comparison not found"
            )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comparison: {str(e)}"
        )


@router.get("/{comparison_id}/status")
async def get_comparison_status(comparison_id: str):
    """
    Get comparison status
    
    - **comparison_id**: The comparison ID
    """
    
    try:
        db = get_database()
        comparison = await db.comparisons.find_one(
            {"_id": ObjectId(comparison_id)},
            {"status": 1, "created_at": 1, "completed_at": 1}
        )
        
        if not comparison:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comparison not found"
            )
        
        return {
            "comparison_id": comparison_id,
            "status": comparison["status"],
            "created_at": comparison["created_at"],
            "completed_at": comparison.get("completed_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.post("/{analysis_id}/compare")
async def compare_from_analysis(analysis_id: str, competitor_urls: List[str]):
    """
    Create comparison from existing analysis
    
    - **analysis_id**: Existing analysis ID
    - **competitor_urls**: List of competitor URLs
    """
    
    try:
        db = get_database()
        
        # Get existing analysis
        analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        
        # Create comparison
        comparison_service = ComparisonService()
        comparison_id = await comparison_service.create_comparison(
            your_url=analysis["website_url"],
            competitor_urls=competitor_urls
        )
        
        return ComparisonResponse(
            comparison_id=comparison_id,
            status="processing",
            message=f"Comparison started from existing analysis"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comparison: {str(e)}"
        )


@router.get("/{comparison_id}/pdf")
async def get_comparison_pdf(comparison_id: str):
    """
    Get or generate comparison PDF report
    
    - **comparison_id**: The comparison ID
    """
    
    try:
        comparison_service = ComparisonService()
        comparison = await comparison_service.get_comparison(comparison_id)
        
        if not comparison:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comparison not found"
            )
        
        # Check if comparison is completed
        if comparison["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Comparison is not completed yet. Status: {comparison['status']}"
            )
        
        # Check if PDF already exists
        if comparison.get("pdf_url"):
            return {
                "pdf_url": comparison["pdf_url"],
                "message": "PDF already generated"
            }
        
        # Generate PDF
        from app.services.comparison_pdf_service import ComparisonPDFService
        
        pdf_service = ComparisonPDFService()
        pdf_path = await pdf_service.generate_comparison_report(comparison)
        
        # Extract filename and create URL
        import os
        pdf_filename = os.path.basename(pdf_path)
        pdf_url = f"/static/pdfs/{pdf_filename}"
        
        # Update comparison with PDF URL
        db = get_database()
        await db.comparisons.update_one(
            {"_id": ObjectId(comparison_id)},
            {"$set": {"pdf_url": pdf_url}}
        )
        
        return {
            "pdf_url": pdf_url,
            "message": "PDF generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.delete("/{comparison_id}")
async def delete_comparison(comparison_id: str):
    """
    Delete a comparison
    
    - **comparison_id**: The comparison ID
    """
    
    try:
        db = get_database()
        result = await db.comparisons.delete_one({"_id": ObjectId(comparison_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comparison not found"
            )
        
        return {"message": "Comparison deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comparison: {str(e)}"
        )
