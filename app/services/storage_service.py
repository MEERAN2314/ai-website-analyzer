import os
import shutil
from typing import Optional
from datetime import datetime

from app.core.config import settings


class StorageService:
    """Service for storing PDF files locally"""
    
    def __init__(self):
        # Create outputs directory for PDFs
        self.output_dir = "outputs/pdfs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create static directory for serving files
        self.static_dir = "app/static/pdfs"
        os.makedirs(self.static_dir, exist_ok=True)
        
        print(f"Storage service initialized: {self.output_dir}")
    
    async def upload_pdf(self, file_path: str, filename: str) -> Optional[str]:
        """
        Store PDF file locally and return access URL
        
        Args:
            file_path: Local path to the PDF file
            filename: Name for the file
            
        Returns:
            URL to access the file, or None if storage fails
        """
        try:
            # Copy to static directory for serving
            dest_path = os.path.join(self.static_dir, filename)
            shutil.copy(file_path, dest_path)
            
            # Also keep in outputs for backup
            backup_path = os.path.join(self.output_dir, filename)
            shutil.copy(file_path, backup_path)
            
            # Return URL to access the file
            file_url = f"/static/pdfs/{filename}"
            print(f"File stored successfully: {file_url}")
            
            return file_url
            
        except Exception as e:
            print(f"Error storing file: {e}")
            return None
    
    async def delete_file(self, filename: str) -> bool:
        """Delete file from storage"""
        try:
            # Delete from static directory
            static_path = os.path.join(self.static_dir, filename)
            if os.path.exists(static_path):
                os.remove(static_path)
            
            # Delete from outputs directory
            output_path = os.path.join(self.output_dir, filename)
            if os.path.exists(output_path):
                os.remove(output_path)
            
            print(f"File deleted successfully: {filename}")
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_path(self, filename: str) -> str:
        """Get full path to stored file"""
        return os.path.join(self.static_dir, filename)
