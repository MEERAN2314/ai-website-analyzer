# Google Drive API Setup Guide

This guide will help you set up Google Drive API credentials for storing PDF reports.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click **"New Project"**
4. Enter project name: `AI Website Analyzer` (or your preferred name)
5. Click **"Create"**
6. Wait for the project to be created (you'll see a notification)

## Step 2: Enable Google Drive API

1. In the Google Cloud Console, make sure your new project is selected
2. Go to **"APIs & Services"** > **"Library"** (or search for "API Library")
3. Search for **"Google Drive API"**
4. Click on **"Google Drive API"**
5. Click **"Enable"** button
6. Wait for the API to be enabled

## Step 3: Create Service Account

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** at the top
3. Select **"Service Account"**
4. Fill in the details:
   - **Service account name:** `website-analyzer-storage`
   - **Service account ID:** (auto-generated)
   - **Description:** `Service account for storing PDF reports`
5. Click **"Create and Continue"**
6. For **"Grant this service account access to project"**:
   - Select role: **"Basic"** > **"Editor"** (or just skip this step)
7. Click **"Continue"**
8. Click **"Done"**

## Step 4: Create and Download Service Account Key

1. In the **"Credentials"** page, find your service account in the list
2. Click on the service account email (e.g., `website-analyzer-storage@...`)
3. Go to the **"Keys"** tab
4. Click **"Add Key"** > **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"**
7. A JSON file will be downloaded automatically
8. **IMPORTANT:** Keep this file secure! It contains sensitive credentials

## Step 5: Rename and Move the Key File

```bash
# Rename the downloaded file to service-account-key.json
mv ~/Downloads/your-project-name-xxxxx.json service-account-key.json

# Move it to your project root directory
mv service-account-key.json /path/to/ai-website-analyzer/
```

## Step 6: Create Google Drive Folder

1. Go to [Google Drive](https://drive.google.com/)
2. Click **"New"** > **"Folder"**
3. Name it: `Website Analyzer Reports` (or your preferred name)
4. Click **"Create"**
5. Open the folder you just created
6. Look at the URL in your browser:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                           ^^^^^^^^^^^^^^^^^^^^
                                           This is your FOLDER_ID
   ```
7. Copy the folder ID (the part after `/folders/`)

## Step 7: Share Folder with Service Account

**IMPORTANT:** You must share the folder with your service account!

1. Right-click on the folder in Google Drive
2. Click **"Share"**
3. In the "Add people and groups" field, paste your service account email:
   - Find it in the downloaded JSON file: look for `"client_email"`
   - It looks like: `website-analyzer-storage@your-project.iam.gserviceaccount.com`
4. Set permission to **"Editor"**
5. **Uncheck** "Notify people" (service accounts don't need notifications)
6. Click **"Share"**

## Step 8: Update .env File

```bash
# Edit your .env file
nano .env
```

Update these lines:
```env
# Google Drive API (for PDF storage)
GOOGLE_DRIVE_CREDENTIALS_FILE="service-account-key.json"
GOOGLE_DRIVE_FOLDER_ID="1a2b3c4d5e6f7g8h9i0j"  # Your folder ID from Step 6
```

## Step 9: Verify Setup

Create a test script to verify everything works:

```python
# test_drive.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

# Load credentials
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'service-account-key.json'
FOLDER_ID = 'YOUR_FOLDER_ID_HERE'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

# Create a test file
with open('test.txt', 'w') as f:
    f.write('Test file for Google Drive API')

# Upload test file
file_metadata = {
    'name': 'test.txt',
    'parents': [FOLDER_ID]
}
media = MediaFileUpload('test.txt', mimetype='text/plain')

file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id, webViewLink'
).execute()

print(f"File uploaded successfully!")
print(f"File ID: {file.get('id')}")
print(f"View Link: {file.get('webViewLink')}")

# Clean up
os.remove('test.txt')
```

Run the test:
```bash
python test_drive.py
```

If successful, you'll see the file ID and link. Check your Google Drive folder to confirm!

## Troubleshooting

### Error: "The caller does not have permission"
**Solution:** Make sure you shared the folder with the service account email (Step 7)

### Error: "File not found: service-account-key.json"
**Solution:** 
- Check the file is in the project root directory
- Verify the filename matches exactly
- Check file permissions: `chmod 600 service-account-key.json`

### Error: "Invalid credentials"
**Solution:**
- Re-download the service account key
- Make sure you're using the correct JSON file
- Verify the JSON file is not corrupted

### Error: "API has not been enabled"
**Solution:** Go back to Step 2 and enable Google Drive API

### Can't find the folder ID
**Solution:** 
- Open the folder in Google Drive
- The URL should be: `https://drive.google.com/drive/folders/FOLDER_ID`
- Copy everything after `/folders/`

## Security Best Practices

1. **Never commit service-account-key.json to Git**
   - It's already in `.gitignore`
   - Double-check before pushing code

2. **Restrict service account permissions**
   - Only grant necessary permissions
   - Use separate service accounts for different environments

3. **Rotate keys regularly**
   - Create new keys every 90 days
   - Delete old keys after rotation

4. **Monitor usage**
   - Check Google Cloud Console for unusual activity
   - Set up billing alerts

5. **Use environment-specific accounts**
   - Different service accounts for dev/staging/production
   - Different folders for each environment

## Alternative: Using OAuth 2.0 (Not Recommended for Server Apps)

If you prefer OAuth 2.0 instead of service accounts:

1. Create OAuth 2.0 credentials instead of service account
2. Download `credentials.json`
3. Run authentication flow to get `token.json`
4. Use `token.json` for API access

**Note:** Service accounts are better for server applications because they don't require user interaction.

## Cost Information

- **Google Drive API:** Free for up to 1 billion requests per day
- **Storage:** 15 GB free per Google account
- **Service Accounts:** Free (no additional cost)

For most applications, you'll stay well within the free tier.

## Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Service Account Documentation](https://cloud.google.com/iam/docs/service-accounts)
- [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python)

## Summary Checklist

- [ ] Created Google Cloud Project
- [ ] Enabled Google Drive API
- [ ] Created Service Account
- [ ] Downloaded service-account-key.json
- [ ] Moved key file to project root
- [ ] Created Google Drive folder
- [ ] Copied folder ID
- [ ] Shared folder with service account email
- [ ] Updated .env file with credentials
- [ ] Tested upload (optional but recommended)
- [ ] Added service-account-key.json to .gitignore (already done)

---

**Need Help?** If you encounter issues, check the troubleshooting section or refer to the official Google Drive API documentation.
