"""
Test registration endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    
    print("=" * 60)
    print("Testing Registration Endpoint")
    print("=" * 60)
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "Test@123456",
        "full_name": "Test User"
    }
    
    print(f"\n📝 Registering user: {test_user['email']}")
    print(f"Password: {test_user['password']}")
    print(f"Full Name: {test_user['full_name']}")
    
    try:
        # Send registration request
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📄 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 201:
            print("\n✅ Registration successful!")
            print("\nNow try logging in:")
            print(f"Email: {test_user['email']}")
            print(f"Password: {test_user['password']}")
        elif response.status_code == 400:
            print("\n⚠️  User might already exist. Try with a different email.")
        else:
            print(f"\n❌ Registration failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_registration()
