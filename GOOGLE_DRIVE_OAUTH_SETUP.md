# Google Drive OAuth 2.0 Setup (Recommended Solution)

## Why OAuth Instead of Service Account?

Service accounts **cannot** upload to personal Google Drive folders due to storage quota limitations. OAuth 2.0 allows your application to access **your** Google Drive storage.

---

## Step-by-Step Setup

### Step 1: Create OAuth 2.0 Credentials

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your project: **bulk-whatsapp-484819**
3. Click **"Create Credentials"** → **"OAuth client ID"**
4. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: **AI Website Analyzer**
   - User support email: Your email
   - Developer contact: Your email
   - Click **Save and Continue**
   - Scopes: Skip for now
   - Test users: Add your email
   - Click **Save and Continue**

5. Back to Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: **Website Analyzer Desktop**
   - Click **Create**

6. Download the JSON file
7. Rename it to: **`credentials.json`**
8. Move it to your project root directory

### Step 2: Install Required Package

```bash
pip install google-auth-oauthlib
```

### Step 3: Run Authentication

```bash
python setup_oauth_drive.py
```

This will:
1. Open your browser
2. Ask you to login to Google
3. Request permission to access Drive
4. Save credentials to `token.pickle`

### Step 4: Test Upload

The script will automatically test uploading a file. You should see:
```
✅ Success! File uploaded!
File ID: xxxxx
View Link: https://drive.google.com/...
```

### Step 5: Update Your Application

Now update your storage service to use OAuth instead of service account.

---

## Alternative: Use Local Storage (Simpler)

If Google Drive is too complex, you can store PDFs locally and serve them:

### Option 1: Local File Storage

```python
# app/services/storage_service.py
import os
from datetime import datetime

class StorageService:
    def __init__(self):
        self.output_dir = "outputs/pdfs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def upload_pdf(self, file_path: str, filename: str) -> str:
        """Store PDF locally and return URL"""
        # Copy to outputs directory
        dest_path = os.path.join(self.output_dir, filename)
        shutil.copy(file_path, dest_path)
        
        # Return URL to access it
        return f"/static/pdfs/{filename}"
```

### Option 2: Database Storage (MongoDB GridFS)

```python
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

class StorageService:
    def __init__(self, db):
        self.fs = AsyncIOMotorGridFSBucket(db)
    
    async def upload_pdf(self, file_path: str, filename: str) -> str:
        """Store PDF in MongoDB GridFS"""
        with open(file_path, 'rb') as f:
            file_id = await self.fs.upload_from_stream(
                filename,
                f,
                metadata={"contentType": "application/pdf"}
            )
        return str(file_id)
```

---

## Recommendation

For your project, I recommend **Option 1: Local File Storage** because:

✅ **Simple** - No external API setup needed
✅ **Fast** - No network latency
✅ **Free** - No storage costs
✅ **Reliable** - No API rate limits
✅ **Works immediately** - No authentication needed

You can always add Google Drive later as an enhancement!

---

## Quick Fix: Update storage_service.py

Let me update your storage service to use local storage instead:
