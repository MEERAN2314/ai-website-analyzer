# Email Setup Guide - SMTP Configuration

## Overview

Email notifications are **optional** but useful for:
- Welcome emails
- Analysis completion notifications
- Password reset
- Scheduled analysis reports

---

## Option 1: Gmail (Recommended for Testing)

### Step 1: Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled

### Step 2: Create App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select app: **Mail**
3. Select device: **Other (Custom name)**
4. Enter name: **Website Analyzer**
5. Click **Generate**
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 3: Update .env File

```env
# Email Configuration
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="abcd efgh ijkl mnop"  # App password (remove spaces)
EMAIL_FROM="your-email@gmail.com"
```

**Important**: Remove spaces from the app password!

### Step 4: Test Email

```bash
python test_email.py
```

---

## Option 2: Gmail with OAuth 2.0 (More Secure)

If you want more security, use OAuth instead of app passwords.

### Requirements:
- Google Cloud Project
- OAuth 2.0 credentials
- More complex setup

**Recommendation**: Use App Password for simplicity.

---

## Option 3: SendGrid (Production Recommended)

SendGrid offers 100 free emails/day.

### Step 1: Create Account

1. Go to: https://signup.sendgrid.com/
2. Sign up for free account
3. Verify your email

### Step 2: Create API Key

1. Go to: https://app.sendgrid.com/settings/api_keys
2. Click **Create API Key**
3. Name: **Website Analyzer**
4. Permissions: **Full Access**
5. Click **Create & View**
6. Copy the API key

### Step 3: Update .env File

```env
# Email Configuration (SendGrid)
SMTP_HOST="smtp.sendgrid.net"
SMTP_PORT=587
SMTP_USER="apikey"  # Literally the word "apikey"
SMTP_PASSWORD="SG.your-api-key-here"
EMAIL_FROM="noreply@yourdomain.com"
```

### Step 4: Verify Sender

1. Go to: https://app.sendgrid.com/settings/sender_auth
2. Click **Verify a Single Sender**
3. Fill in your details
4. Verify your email
5. Use verified email in `EMAIL_FROM`

---

## Option 4: Mailgun (Alternative)

Mailgun offers 5,000 free emails/month.

### Setup:

1. Sign up: https://signup.mailgun.com/
2. Get SMTP credentials
3. Update .env:

```env
SMTP_HOST="smtp.mailgun.org"
SMTP_PORT=587
SMTP_USER="postmaster@your-domain.mailgun.org"
SMTP_PASSWORD="your-mailgun-password"
EMAIL_FROM="noreply@your-domain.mailgun.org"
```

---

## Option 5: Skip Email (For Now)

If you don't need email notifications right now, you can skip this setup. The application will work fine without it.

Just leave the fields empty:

```env
# Email Configuration (Optional - leave empty to disable)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER=""
SMTP_PASSWORD=""
EMAIL_FROM="noreply@websiteanalyzer.com"
```

The app will detect empty credentials and skip email sending.

---

## Testing Email Configuration

### Test Script

```python
# test_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def test_email():
    """Test SMTP configuration"""
    
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM')
    
    if not smtp_user or not smtp_password:
        print("⚠️  Email not configured. Skipping test.")
        return
    
    print(f"📧 Testing email with {smtp_host}:{smtp_port}")
    print(f"From: {email_from}")
    print(f"User: {smtp_user}")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = smtp_user  # Send to yourself
        msg['Subject'] = "Test Email - AI Website Analyzer"
        
        body = """
        <html>
        <body>
            <h2>Email Configuration Test</h2>
            <p>If you're reading this, your email configuration is working! 🎉</p>
            <p>Your AI Website Analyzer is ready to send notifications.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect and send
        print("🔌 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        
        print("🔐 Logging in...")
        server.login(smtp_user, smtp_password)
        
        print("📤 Sending test email...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Success! Check your inbox.")
        print(f"📬 Email sent to: {smtp_user}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your SMTP credentials")
        print("2. For Gmail, use App Password (not regular password)")
        print("3. Ensure 2FA is enabled for Gmail")
        print("4. Check firewall/network settings")

if __name__ == "__main__":
    test_email()
```

### Run Test

```bash
python test_email.py
```

---

## Common Issues & Solutions

### Issue 1: "Username and Password not accepted"

**For Gmail:**
- Make sure you're using an **App Password**, not your regular password
- Enable 2-Factor Authentication first
- Remove spaces from app password

**Solution:**
```env
SMTP_PASSWORD="abcdefghijklmnop"  # No spaces!
```

### Issue 2: "Connection refused"

**Cause:** Firewall or wrong port

**Solution:**
- Try port 465 (SSL) instead of 587 (TLS)
- Check firewall settings
- Try different network

### Issue 3: "Sender address rejected"

**Cause:** Email not verified

**Solution:**
- For SendGrid/Mailgun: Verify sender email
- For Gmail: Use the same email as SMTP_USER

### Issue 4: "Too many login attempts"

**Cause:** Gmail security

**Solution:**
- Wait 15 minutes
- Check: https://accounts.google.com/DisplayUnlockCaptcha
- Allow less secure apps (not recommended)

---

## Email Service Implementation

### Basic Email Service

```python
# app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.enabled = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
    
    async def send_email(self, to: str, subject: str, body: str):
        """Send email notification"""
        
        if not self.enabled:
            print("Email not configured. Skipping.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
```

---

## Recommendation for Your Project

### For Development/Demo:
**Use Gmail with App Password**
- Quick setup (5 minutes)
- Free
- Reliable
- Good for testing

### For Production:
**Use SendGrid or Mailgun**
- Professional
- Better deliverability
- Analytics
- Scalable

### For Now:
**Skip it!**
- Email is optional
- Focus on core features
- Add later if needed

---

## Quick Setup (Gmail)

1. **Enable 2FA**: https://myaccount.google.com/security
2. **Create App Password**: https://myaccount.google.com/apppasswords
3. **Update .env**:
   ```env
   SMTP_USER="your-email@gmail.com"
   SMTP_PASSWORD="your-app-password"
   EMAIL_FROM="your-email@gmail.com"
   ```
4. **Test**: `python test_email.py`

---

## Summary

| Service | Free Tier | Setup Time | Best For |
|---------|-----------|------------|----------|
| Gmail | Unlimited | 5 min | Development |
| SendGrid | 100/day | 10 min | Production |
| Mailgun | 5000/month | 10 min | Production |
| Skip | N/A | 0 min | MVP/Demo |

**My Recommendation**: Skip for now, add Gmail later if needed.

Your app works perfectly without email! 🚀
