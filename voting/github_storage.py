"""
GitHub storage service for candidate images.
Provides free cloud storage using GitHub repositories.
"""

import requests
import base64
import logging
from django.conf import settings
import os
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class GitHubStorageService:
    """Service for uploading images to GitHub repository for free cloud storage."""
    
    def __init__(self):
        self.github_token = getattr(settings, 'GITHUB_TOKEN', None)
        self.github_repo = getattr(settings, 'GITHUB_IMAGES_REPO', None)  # format: "username/repo-name"
        self.github_branch = getattr(settings, 'GITHUB_IMAGES_BRANCH', 'main')
        self.api_base_url = 'https://api.github.com/repos'
        
    def upload_image(self, image_file, candidate_reg_no, title=None):
        """
        Upload an image to GitHub repository and return the raw URL.
        
        Args:
            image_file: Django file object or file path
            candidate_reg_no: Registration number for unique filename
            title: Optional title for the image
            
        Returns:
            str: Raw GitHub URL of uploaded image or None if failed
        """
        if not self.is_configured():
            logger.warning("GitHub storage not configured. Using local storage fallback.")
            return None
            
        try:
            # Read image data
            if hasattr(image_file, 'read'):
                # Django file object
                image_data = image_file.read()
                image_file.seek(0)  # Reset file pointer
                filename = getattr(image_file, 'name', f'candidate_{candidate_reg_no}.jpg')
            else:
                # File path
                with open(image_file, 'rb') as f:
                    image_data = f.read()
                filename = os.path.basename(image_file)
            
            # Create unique filename
            file_extension = os.path.splitext(filename)[1] or '.jpg'
            safe_filename = f"candidate_{candidate_reg_no}{file_extension}"
            file_path = f"candidates/{safe_filename}"
            
            # Encode to base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare GitHub API request
            url = f"{self.api_base_url}/{self.github_repo}/contents/{file_path}"
            
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            # Check if file already exists (to get SHA for update)
            existing_file_sha = self._get_file_sha(file_path)
            
            data = {
                'message': f'Upload candidate photo: {candidate_reg_no}',
                'content': image_b64,
                'branch': self.github_branch
            }
            
            # Add SHA if file exists (for update)
            if existing_file_sha:
                data['sha'] = existing_file_sha
                logger.info(f"Updating existing image for {candidate_reg_no}")
            else:
                logger.info(f"Uploading new image for {candidate_reg_no}")
            
            # Make request to GitHub API
            response = requests.put(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                # Generate raw URL
                raw_url = f"https://raw.githubusercontent.com/{self.github_repo}/{self.github_branch}/{file_path}"
                logger.info(f"Successfully uploaded image to GitHub: {raw_url}")
                return raw_url
            else:
                logger.error(f"GitHub upload failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error uploading to GitHub: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to GitHub: {e}")
            return None
    
    def _get_file_sha(self, file_path):
        """Get SHA of existing file for updates."""
        if not self.is_configured():
            return None
            
        try:
            url = f"{self.api_base_url}/{self.github_repo}/contents/{file_path}"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json().get('sha')
            return None
        except Exception:
            return None
    
    def delete_image(self, file_path):
        """Delete an image from GitHub repository."""
        if not self.is_configured():
            return False
            
        try:
            # Get file SHA first
            file_sha = self._get_file_sha(file_path)
            if not file_sha:
                return False
                
            url = f"{self.api_base_url}/{self.github_repo}/contents/{file_path}"
            headers = {
                'Authorization': f'Bearer {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'message': f'Delete image: {file_path}',
                'sha': file_sha,
                'branch': self.github_branch
            }
            
            response = requests.delete(url, headers=headers, json=data, timeout=30)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error deleting image from GitHub: {e}")
            return False
    
    def is_configured(self):
        """Check if GitHub storage is properly configured."""
        return bool(self.github_token and self.github_repo)
    
    def get_raw_url(self, file_path):
        """Generate raw URL for a file path."""
        if not self.github_repo:
            return None
        return f"https://raw.githubusercontent.com/{self.github_repo}/{self.github_branch}/{file_path}"


# Global instance
github_storage = GitHubStorageService()
