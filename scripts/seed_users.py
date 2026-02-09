"""
Seed script to create sample users for testing
Run with: python scripts/seed_users.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.security import get_password_hash


async def seed_users():
    """Create sample users for all plans"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    users = [
        {
            "email": "basic@example.com",
            "hashed_password": get_password_hash("Basic@123"),
            "full_name": "Basic User",
            "plan": "basic",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "analyses_count": 5,
            "monthly_analyses_count": 5,
            "monthly_reset_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "email": "pro@example.com",
            "hashed_password": get_password_hash("Pro@123"),
            "full_name": "Pro User",
            "plan": "pro",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "analyses_count": 25,
            "monthly_analyses_count": 25,
            "monthly_reset_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "email": "enterprise@example.com",
            "hashed_password": get_password_hash("Enterprise@123"),
            "full_name": "Enterprise User",
            "plan": "enterprise",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "analyses_count": 100,
            "monthly_analyses_count": 100,
            "monthly_reset_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "email": "admin@example.com",
            "hashed_password": get_password_hash("Admin@123"),
            "full_name": "Admin User",
            "plan": "enterprise",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "analyses_count": 0,
            "monthly_analyses_count": 0,
            "monthly_reset_date": datetime.utcnow() + timedelta(days=30)
        }
    ]
    
    print("Seeding users...")
    
    for user in users:
        # Check if user exists
        existing = await db.users.find_one({"email": user["email"]})
        
        if existing:
            print(f"✓ User {user['email']} already exists")
        else:
            await db.users.insert_one(user)
            print(f"✓ Created user: {user['email']} (Plan: {user['plan']})")
    
    print("\nSample credentials:")
    print("=" * 50)
    print("Basic Plan:")
    print("  Email: basic@example.com")
    print("  Password: Basic@123")
    print("\nPro Plan:")
    print("  Email: pro@example.com")
    print("  Password: Pro@123")
    print("\nEnterprise Plan:")
    print("  Email: enterprise@example.com")
    print("  Password: Enterprise@123")
    print("\nAdmin:")
    print("  Email: admin@example.com")
    print("  Password: Admin@123")
    print("=" * 50)
    
    client.close()
    print("\n✓ Seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_users())
