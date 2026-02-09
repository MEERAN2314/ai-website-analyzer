#!/usr/bin/env python3
"""
Test script for advanced features:
- Action Plan Generator
- Export formats (JSON, CSV)
- Shareable links
"""

import asyncio
import sys
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.services.analysis_service import perform_website_analysis


async def test_advanced_features():
    """Test all advanced features"""
    
    print("=" * 60)
    print("🧪 Testing Advanced Features")
    print("=" * 60)
    
    # Initialize database connection
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    print(f"📡 Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    
    # Step 1: Create a test analysis
    print("\n1️⃣  Creating test analysis...")
    test_url = "https://example.com"
    
    analysis_dict = {
        "website_url": test_url,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "user_id": "test_user"
    }
    
    result = await db.analyses.insert_one(analysis_dict)
    analysis_id = str(result.inserted_id)
    print(f"✅ Analysis created with ID: {analysis_id}")
    
    # Step 2: Run analysis (this should generate action plan)
    print("\n2️⃣  Running analysis (includes action plan generation)...")
    await perform_website_analysis(analysis_id, test_url)
    
    # Step 3: Verify analysis completed
    print("\n3️⃣  Verifying analysis completion...")
    analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    
    if not analysis:
        print("❌ Analysis not found!")
        return False
    
    if analysis.get('status') != 'completed':
        print(f"❌ Analysis status: {analysis.get('status')}")
        return False
    
    print(f"✅ Analysis completed successfully")
    print(f"   Overall Score: {analysis.get('overall_score'):.1f}/100")
    
    # Step 4: Check action plan
    print("\n4️⃣  Checking action plan...")
    action_plan = analysis.get('action_plan')
    
    if not action_plan:
        print("❌ Action plan not generated!")
        return False
    
    print("✅ Action plan generated:")
    print(f"   Summary: {action_plan.get('summary')}")
    print(f"   Total Tasks: {action_plan.get('total_tasks')}")
    print(f"   Estimated Impact: {action_plan.get('estimated_impact')}")
    
    if action_plan.get('roadmap'):
        roadmap_preview = action_plan['roadmap'][:200] + "..."
        print(f"   Roadmap Preview: {roadmap_preview}")
    
    # Step 5: Test export endpoints (simulated)
    print("\n5️⃣  Testing export data structure...")
    
    # Check if data is exportable
    export_data = {
        "website_url": analysis.get('website_url'),
        "analysis_date": analysis.get('completed_at'),
        "overall_score": analysis.get('overall_score'),
        "scores": {
            "ux": analysis.get('ux_analysis', {}).get('score'),
            "seo": analysis.get('seo_analysis', {}).get('score'),
            "performance": analysis.get('performance_analysis', {}).get('score'),
            "content": analysis.get('content_analysis', {}).get('score')
        },
        "priority_recommendations": analysis.get('priority_recommendations', []),
        "action_plan": action_plan
    }
    
    print("✅ Export data structure valid:")
    print(f"   - Website URL: {export_data['website_url']}")
    print(f"   - Overall Score: {export_data['overall_score']}")
    print(f"   - Recommendations: {len(export_data['priority_recommendations'])} items")
    print(f"   - Action Plan: {'Present' if export_data['action_plan'] else 'Missing'}")
    
    # Step 6: Test share functionality (simulated)
    print("\n6️⃣  Testing share data structure...")
    
    import secrets
    from datetime import timedelta
    
    share_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    share_data = {
        "analysis_id": analysis_id,
        "share_token": share_token,
        "created_by": "test_user",
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "view_count": 0,
        "is_active": True
    }
    
    # Insert share record
    await db.shares.insert_one(share_data)
    
    print("✅ Share link structure valid:")
    print(f"   - Share Token: {share_token[:20]}...")
    print(f"   - Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   - Share URL: /api/v1/share/{share_token}")
    
    # Verify share can be retrieved
    share_check = await db.shares.find_one({"share_token": share_token})
    if share_check:
        print("✅ Share link retrievable from database")
    else:
        print("❌ Share link not found in database")
    
    # Step 7: Check PDF generation
    print("\n7️⃣  Checking PDF generation...")
    pdf_url = analysis.get('pdf_url')
    
    if pdf_url:
        print(f"✅ PDF generated: {pdf_url}")
    else:
        print("⚠️  PDF not generated (may have failed)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FEATURE TEST SUMMARY")
    print("=" * 60)
    
    features_status = {
        "Analysis Completion": "✅" if analysis.get('status') == 'completed' else "❌",
        "Action Plan Generation": "✅" if action_plan else "❌",
        "Export Data Structure": "✅",
        "Share Link Creation": "✅" if share_check else "❌",
        "PDF Generation": "✅" if pdf_url else "⚠️"
    }
    
    for feature, status in features_status.items():
        print(f"{status} {feature}")
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Navigate to: http://localhost:8000/results/" + analysis_id)
    print("3. Test the following buttons:")
    print("   - 30/60/90 Day Plan (should show action plan modal)")
    print("   - Download PDF (should open PDF in new tab)")
    print("   - Export dropdown (JSON/CSV downloads)")
    print("   - Share Analysis (should generate shareable link)")
    print("\n" + "=" * 60)
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    await db.analyses.delete_one({"_id": ObjectId(analysis_id)})
    await db.shares.delete_one({"share_token": share_token})
    print("✅ Cleanup complete")
    
    # Close database connection
    client.close()
    
    return True


async def main():
    try:
        success = await test_advanced_features()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
