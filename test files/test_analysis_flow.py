"""
Test the complete analysis flow
"""
import asyncio
from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.services.analysis_service import perform_website_analysis
from bson import ObjectId
from datetime import datetime


async def test_analysis():
    """Test analysis flow"""
    print("🧪 Testing Analysis Flow\n")
    
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Create a test analysis record
    test_url = "https://example.com"
    print(f"📊 Creating test analysis for: {test_url}")
    
    analysis_dict = {
        "user_id": None,  # Guest user
        "website_url": test_url,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = await db.analyses.insert_one(analysis_dict)
    analysis_id = str(result.inserted_id)
    print(f"✅ Analysis created with ID: {analysis_id}\n")
    
    # Run the analysis
    print("🔍 Starting analysis...")
    try:
        await perform_website_analysis(analysis_id, test_url)
        print("✅ Analysis completed!\n")
        
        # Fetch the results
        analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
        
        print("📈 Results:")
        print(f"  Status: {analysis.get('status')}")
        print(f"  Overall Score: {analysis.get('overall_score')}/100")
        print(f"  UX Score: {analysis.get('ux_analysis', {}).get('score')}/100")
        print(f"  SEO Score: {analysis.get('seo_analysis', {}).get('score')}/100")
        print(f"  Performance Score: {analysis.get('performance_analysis', {}).get('score')}/100")
        print(f"  Content Score: {analysis.get('content_analysis', {}).get('score')}/100")
        
        if analysis.get('status') == 'completed':
            print("\n✨ Analysis successful!")
            print(f"\n📝 AI Summary (first 200 chars):")
            print(analysis.get('ai_summary', 'N/A')[:200] + "...")
        else:
            print(f"\n❌ Analysis failed: {analysis.get('error_message')}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close database connection
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(test_analysis())
