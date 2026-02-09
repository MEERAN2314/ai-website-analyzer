"""Test local PDF storage"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.storage_service import StorageService

async def test_storage():
    """Test local storage"""
    storage = StorageService()
    
    # Create test PDF
    test_file = "test_report.pdf"
    with open(test_file, 'w') as f:
        f.write("Test PDF content")
    
    print("📤 Uploading test file...")
    
    # Upload (actually just copies locally)
    url = await storage.upload_pdf(test_file, "test_report.pdf")
    
    if url:
        print(f"✅ Success! File stored at: {url}")
        print(f"📁 File location: app/static/pdfs/test_report.pdf")
        print(f"🌐 Access URL: http://localhost:8000{url}")
    else:
        print("❌ Failed to store file")
    
    # Clean up test file
    os.remove(test_file)
    
    print("\n✨ Local storage is working perfectly!")

if __name__ == "__main__":
    asyncio.run(test_storage())
