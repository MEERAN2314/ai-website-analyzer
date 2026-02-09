from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from bson import ObjectId
import csv
import io
import json
from datetime import datetime

from app.core.database import get_database

router = APIRouter()


@router.get("/{analysis_id}/csv")
async def export_csv(analysis_id: str):
    """Export analysis as CSV"""
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
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Website Analysis Report'])
    writer.writerow(['Website', analysis.get('website_url')])
    writer.writerow(['Date', analysis.get('completed_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Scores
    writer.writerow(['Metric', 'Score'])
    writer.writerow(['Overall Score', f"{analysis.get('overall_score', 0):.1f}"])
    writer.writerow(['UX Score', f"{analysis.get('ux_analysis', {}).get('score', 0):.1f}"])
    writer.writerow(['SEO Score', f"{analysis.get('seo_analysis', {}).get('score', 0):.1f}"])
    writer.writerow(['Performance Score', f"{analysis.get('performance_analysis', {}).get('score', 0):.1f}"])
    writer.writerow(['Content Score', f"{analysis.get('content_analysis', {}).get('score', 0):.1f}"])
    writer.writerow([])
    
    # Priority Recommendations
    writer.writerow(['Priority Recommendations'])
    writer.writerow(['Title', 'Description', 'Priority', 'Impact', 'Effort', 'Category'])
    for rec in analysis.get('priority_recommendations', []):
        writer.writerow([
            rec.get('title', ''),
            rec.get('description', ''),
            rec.get('priority', ''),
            rec.get('impact', ''),
            rec.get('effort', ''),
            rec.get('category', '')
        ])
    writer.writerow([])
    
    # Issues by category
    for category in ['ux_analysis', 'seo_analysis', 'performance_analysis', 'content_analysis']:
        cat_data = analysis.get(category, {})
        cat_name = category.replace('_analysis', '').upper()
        
        writer.writerow([f'{cat_name} Issues'])
        for issue in cat_data.get('issues', []):
            writer.writerow([issue])
        writer.writerow([])
        
        writer.writerow([f'{cat_name} Recommendations'])
        for rec in cat_data.get('recommendations', []):
            writer.writerow([rec])
        writer.writerow([])
    
    # Get CSV content
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=analysis_{analysis_id}.csv"
        }
    )


@router.get("/{analysis_id}/json")
async def export_json(analysis_id: str):
    """Export analysis as JSON"""
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
    
    # Clean export data
    export_data = {
        "website_url": analysis.get('website_url'),
        "analysis_date": analysis.get('completed_at', datetime.utcnow()).isoformat(),
        "overall_score": analysis.get('overall_score'),
        "scores": {
            "ux": analysis.get('ux_analysis', {}).get('score'),
            "seo": analysis.get('seo_analysis', {}).get('score'),
            "performance": analysis.get('performance_analysis', {}).get('score'),
            "content": analysis.get('content_analysis', {}).get('score')
        },
        "ai_summary": analysis.get('ai_summary'),
        "priority_recommendations": analysis.get('priority_recommendations', []),
        "action_plan": analysis.get('action_plan'),
        "detailed_analysis": {
            "ux": analysis.get('ux_analysis'),
            "seo": analysis.get('seo_analysis'),
            "performance": analysis.get('performance_analysis'),
            "content": analysis.get('content_analysis')
        }
    }
    
    return Response(
        content=json.dumps(export_data, indent=2, default=str),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=analysis_{analysis_id}.json"
        }
    )


@router.get("/{analysis_id}/action-plan")
async def get_action_plan(analysis_id: str):
    """Get 30/60/90 day action plan"""
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
    
    action_plan = analysis.get('action_plan')
    
    if not action_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action plan not generated yet"
        )
    
    return action_plan
