"""
Setup Google Drive with OAuth 2.0 (User Authentication)
This is the recommended approach for personal Google accounts
"""
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Get authenticated Drive service"""
    creds = None
    
    # Token file stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You need to create OAuth credentials first
            print("⚠️  OAuth credentials not found!")
            print("\nPlease follow these steps:")
            print("1. Go to: https://console.cloud.google.com/apis/credentials")
            print("2. Click 'Create Credentials' → 'OAuth client ID'")
            print("3. Choose 'Desktop app'")
            print("4. Download the JSON file")
            print("5. Rename it to 'credentials.json'")
            print("6. Place it in this directory")
            print("7. Run this script again")
            return None
            
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def test_upload():
    """Test file upload"""
    service = get_drive_service()
    if not service:
        return
    
    # Create test file
    with open('test.txt', 'w') as f:
        f.write('Test upload from AI Website Analyzer')
    
    # Upload to your folder
    file_metadata = {
        'name': 'test.txt',
        'parents': ['1xIo0Yh7dGyOhgbnA_Gj1khHEQZi8FpLM']
    }
    media = MediaFileUpload('test.txt', mimetype='text/plain')
    
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        print(f"✅ Success! File uploaded!")
        print(f"File ID: {file.get('id')}")
        print(f"View Link: {file.get('webViewLink')}")
        
        # Clean up
        os.remove('test.txt')
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_upload()
