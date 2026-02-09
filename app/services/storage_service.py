from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from typing import Optional
import os

from app.core.config import settings


class StorageService:
    """Service for uploading files to Google Drive"""
    
    def __init__(self):
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Drive service"""
        try:
            if not os.path.exists(settings.GOOGLE_DRIVE_CREDENTIALS_FILE):
                print(f"Warning: Google Drive credentials file not found: {settings.GOOGLE_DRIVE_CREDENTIALS_FILE}")
                return
            
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_DRIVE_CREDENTIALS_FILE,
                scopes=SCOPES
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            print("Google Drive service initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Google Drive service: {e}")
            self.service = None
    
    async def upload_pdf(self, file_path: str, filename: str) -> Optional[str]:
        """
        Upload PDF file to Google Drive
        
        Args:
            file_path: Local path to the PDF file
            filename: Name for the file in Google Drive
            
        Returns:
            Web view link to the uploaded file, or None if upload fails
        """
        if not self.service:
            print("Google Drive service not initialized. Skipping upload.")
            return None
        
        if not settings.GOOGLE_DRIVE_FOLDER_ID:
            print("Google Drive folder ID not configured. Skipping upload.")
            return None
        
        try:
            file_metadata = {
                'name': filename,
                'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
            }
            
            media = MediaFileUpload(
                file_path,
                mimetype='application/pdf',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            print(f"File uploaded successfully: {file.get('webViewLink')}")
            return file.get('webViewLink')
            
        except Exception as e:
            print(f"Error uploading file to Google Drive: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive"""
        if not self.service:
            return False
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"File deleted successfully: {file_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting file from Google Drive: {e}")
            return False
