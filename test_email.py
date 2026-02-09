"""
Test email configuration
"""
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
        print("⚠️  Email not configured. This is optional.")
        print("\nTo configure email:")
        print("1. See EMAIL_SETUP_GUIDE.md")
        print("2. For Gmail: Use App Password")
        print("3. Update SMTP_USER and SMTP_PASSWORD in .env")
        print("\nYour app works fine without email! 🚀")
        return
    
    print(f"📧 Testing email configuration...")
    print(f"Host: {smtp_host}:{smtp_port}")
    print(f"From: {email_from}")
    print(f"User: {smtp_user}")
    print()
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = smtp_user  # Send to yourself
        msg['Subject'] = "✅ Test Email - AI Website Analyzer"
        
        body = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2563EB;">🎉 Email Configuration Test</h2>
            <p>If you're reading this, your email configuration is working perfectly!</p>
            <p>Your <strong>AI Website Analyzer</strong> is ready to send notifications.</p>
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="color: #666; font-size: 14px;">
                This is a test email from your AI Website Analyzer application.
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect and send
        print("🔌 Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        
        print("🔐 Authenticating...")
        server.login(smtp_user, smtp_password)
        
        print("📤 Sending test email...")
        server.send_message(msg)
        server.quit()
        
        print("\n✅ Success! Email sent successfully!")
        print(f"📬 Check your inbox: {smtp_user}")
        print("\nYour email configuration is working! 🎉")
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ Authentication failed!")
        print("\nFor Gmail:")
        print("1. Enable 2-Factor Authentication")
        print("2. Create App Password: https://myaccount.google.com/apppasswords")
        print("3. Use App Password (not regular password)")
        print("4. Remove spaces from app password")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your SMTP credentials in .env")
        print("2. For Gmail, use App Password (not regular password)")
        print("3. Ensure 2FA is enabled for Gmail")
        print("4. Check firewall/network settings")
        print("5. See EMAIL_SETUP_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    print("=" * 60)
    print("  AI Website Analyzer - Email Configuration Test")
    print("=" * 60)
    print()
    test_email()
    print()
    print("=" * 60)
