"""
Check MongoDB connection
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def check_mongodb():
    """Check if MongoDB is accessible"""
    
    print("=" * 60)
    print("Checking MongoDB Connection")
    print("=" * 60)
    
    print(f"\n📡 MongoDB URL: {settings.MONGODB_URL}")
    print(f"📦 Database Name: {settings.MONGODB_DB_NAME}")
    
    try:
        # Connect to MongoDB
        print("\n🔌 Connecting to MongoDB...")
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database
        db = client[settings.MONGODB_DB_NAME]
        
        # List collections
        collections = await db.list_collection_names()
        print(f"\n📚 Collections in database:")
        if collections:
            for coll in collections:
                count = await db[coll].count_documents({})
                print(f"  - {coll}: {count} documents")
        else:
            print("  (No collections yet)")
        
        # Check users collection
        users_count = await db.users.count_documents({})
        print(f"\n👥 Total users: {users_count}")
        
        if users_count > 0:
            print("\n📋 Sample users:")
            async for user in db.users.find().limit(5):
                print(f"  - {user.get('email')} ({user.get('plan')})")
        
        client.close()
        print("\n✅ MongoDB is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ MongoDB connection failed!")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if MongoDB is running")
        print("2. Verify MONGODB_URL in .env file")
        print("3. For MongoDB Atlas:")
        print("   - Check IP whitelist (allow 0.0.0.0/0 for testing)")
        print("   - Verify username/password")
        print("   - Check network connection")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_mongodb())
    sys.exit(0 if result else 1)
