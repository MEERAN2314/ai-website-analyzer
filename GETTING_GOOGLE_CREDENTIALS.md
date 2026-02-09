# How to Get Google Credentials - Simple Guide

## What You Need

1. **Google Gemini API Key** (Required) - For AI analysis
2. **Google Drive Credentials** (Optional) - For PDF storage

---

## Part 1: Google Gemini API Key (REQUIRED)

### Step 1: Get Your API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Select **"Create API key in new project"** (or use existing project)
4. Copy the API key (starts with `AIza...`)

### Step 2: Add to .env File

Open your `.env` file and add:

```env
GOOGLE_API_KEY="AIzaSyD_your_actual_api_key_here"
```

**That's it!** You can now use the AI analysis features.

### Troubleshooting Gemini API

**Error: "API key not valid"**
- Make sure you copied the entire key
- No spaces before/after the key
- No quotes inside the .env value

**Error: "Quota exceeded"**
- Free tier: 60 requests per minute
- Wait a minute and try again
- Or upgrade to paid tier

---

## Part 2: Google Drive API (OPTIONAL - For PDF Storage)

**Note:** This is optional. The app works without it, but PDFs won't be stored in Google Drive.

### Quick Overview
1. Create Google Cloud Project (2 min)
2. Enable Google Drive API (1 min)
3. Create Service Account (2 min)
4. Download JSON key file (1 min)
5. Create Drive folder & share it (2 min)

### Detailed Steps

#### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click project dropdown (top left)
3. Click **"NEW PROJECT"**
4. Name: `Website Analyzer`
5. Click **"CREATE"**

#### Step 2: Enable Google Drive API

1. In the search bar, type: `Google Drive API`
2. Click on **"Google Drive API"**
3. Click **"ENABLE"**

#### Step 3: Create Service Account

1. Go to: **APIs & Services** > **Credentials**
2. Click **"CREATE CREDENTIALS"**
3. Select **"Service Account"**
4. Name: `pdf-storage`
5. Click **"CREATE AND CONTINUE"**
6. Skip optional steps, click **"DONE"**

#### Step 4: Download Key File

1. In Credentials page, find your service account
2. Click on the service account email
3. Go to **"KEYS"** tab
4. Click **"ADD KEY"** > **"Create new key"**
5. Choose **"JSON"**
6. Click **"CREATE"**
7. File downloads automatically

#### Step 5: Move Key File

```bash
# Rename the downloaded file
mv ~/Downloads/website-analyzer-*.json service-account-key.json

# Move to project root
mv service-account-key.json /path/to/ai-website-analyzer/
```

#### Step 6: Create Google Drive Folder

1. Go to: https://drive.google.com/
2. Click **"New"** > **"Folder"**
3. Name: `Website Reports`
4. Open the folder
5. Copy the folder ID from URL:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                           ^^^^^^^^^^^^^^^^^^^^
                                           This is your folder ID
   ```

#### Step 7: Share Folder with Service Account

**CRITICAL STEP - Don't skip!**

1. Right-click the folder
2. Click **"Share"**
3. Paste your service account email:
   - Open `service-account-key.json`
   - Find `"client_email"` value
   - It looks like: `pdf-storage@website-analyzer.iam.gserviceaccount.com`
4. Set permission: **"Editor"**
5. Uncheck **"Notify people"**
6. Click **"Share"**

#### Step 8: Update .env File

```env
GOOGLE_DRIVE_CREDENTIALS_FILE="service-account-key.json"
GOOGLE_DRIVE_FOLDER_ID="1a2b3c4d5e6f7g8h9i0j"
```

### Test It Works

Create `test_drive.py`:

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.file']
credentials = service_account.Credentials.from_service_account_file(
    'service-account-key.json', scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)
print("✓ Google Drive connected successfully!")
```

Run it:
```bash
python test_drive.py
```

---

## Summary

### Minimum Required (App will work):
```env
GOOGLE_API_KEY="AIzaSyD_your_key_here"
```

### Full Features (with PDF storage):
```env
GOOGLE_API_KEY="AIzaSyD_your_key_here"
GOOGLE_DRIVE_CREDENTIALS_FILE="service-account-key.json"
GOOGLE_DRIVE_FOLDER_ID="your_folder_id_here"
```

---

## Quick Checklist

**For Gemini API:**
- [ ] Got API key from makersuite.google.com
- [ ] Added to .env file
- [ ] Tested with a simple analysis

**For Google Drive (Optional):**
- [ ] Created Google Cloud project
- [ ] Enabled Google Drive API
- [ ] Created service account
- [ ] Downloaded JSON key file
- [ ] Moved file to project root
- [ ] Created Drive folder
- [ ] Copied folder ID
- [ ] Shared folder with service account email
- [ ] Updated .env file

---

## Need Help?

**Gemini API Issues:**
- Check: https://ai.google.dev/tutorials/setup
- Verify billing is enabled (if required)

**Google Drive Issues:**
- Make sure folder is shared with service account
- Check service account email in JSON file
- Verify folder ID is correct

**Still Stuck?**
- See `GOOGLE_DRIVE_SETUP.md` for detailed guide
- Check `SETUP_GUIDE.md` for troubleshooting
- Open an issue on GitHub

---

**Remember:** Google Drive setup is optional. The app works great with just the Gemini API key!
