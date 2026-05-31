"""
Download Manager for ClassPlus Telegram Bot
Handles file downloads, HLS/M3U8 streams, and progress tracking
"""

import os
import subprocess
import logging
from typing import Callable, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DownloadManager:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        self._create_directory()
    
    def _create_directory(self):
        """Create download directory if it doesn't exist"""
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename"""
        import re
        return re.sub(r'[\\/*?:"<>|]', '', filename)
    
    def download_file(
        self,
        url: str,
        filename: str,
        progress_callback: Optional[Callable] = None,
        timeout: int = 300
    ) -> tuple:
        """
        Download a file with progress tracking
        Returns: (success, filepath, error_message)
        """
        try:
            import requests
            
            filename = self.sanitize_filename(filename)
            filepath = os.path.join(self.download_dir, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                return True, filepath, "File already exists"
            
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            downloaded = 0
            chunk_size = 8192
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress, downloaded, total_size)
            
            return True, filepath, "Downloaded successfully"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Download error: {e}")
            return False, "", str(e)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, "", str(e)
    
    def download_m3u8(
        self,
        url: str,
        filepath: str,
        progress_callback: Optional[Callable] = None
    ) -> tuple:
        """
        Download HLS/M3U8 stream using ffmpeg
        Returns: (success, filepath, error_message)
        """
        try:
            filepath = self.sanitize_filename(filepath)
            full_path = os.path.join(self.download_dir, filepath)
            
            # Check if ffmpeg is installed
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, timeout=5)
            if result.returncode != 0:
                return False, "", "FFmpeg not installed"
            
            # Download using ffmpeg
            command = [
                'ffmpeg',
                '-i', url,
                '-c', 'copy',
                '-bsf:a', 'aac_adtstoasc',
                full_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(full_path):
                return True, full_path, "Downloaded successfully"
            else:
                error = result.stderr or "Unknown ffmpeg error"
                return False, "", error
        
        except FileNotFoundError:
            return False, "", "FFmpeg not found. Install with: pip install ffmpeg-python"
        except subprocess.TimeoutExpired:
            return False, "", "FFmpeg command timed out"
        except Exception as e:
            logger.error(f"M3U8 download error: {e}")
            return False, "", str(e)
    
    def get_file_size(self, filepath: str) -> str:
        """Get human-readable file size"""
        try:
            size = os.path.getsize(filepath)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown"
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """Delete files older than specified days"""
        import time
        
        deleted_count = 0
        now = time.time()
        cutoff = now - (days * 24 * 60 * 60)
        
        try:
            for filename in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff:
                        os.remove(filepath)
                        deleted_count += 1
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        
        return deleted_count
    
    def list_downloads(self) -> list:
        """List all downloaded files"""
        try:
            files = []
            for filename in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, filename)
                if os.path.isfile(filepath):
                    size = self.get_file_size(filepath)
                    files.append({
                        'name': filename,
                        'size': size,
                        'path': filepath
                    })
            return files
        except:
            return []
    
    def get_total_size(self) -> str:
        """Get total size of all downloads"""
        try:
            total = 0
            for filename in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, filename)
                if os.path.isfile(filepath):
                    total += os.path.getsize(filepath)
            return self.format_size(total)
        except:
            return "Unknown"
    
    @staticmethod
    def format_size(size: int) -> str:
        """Format size in bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
