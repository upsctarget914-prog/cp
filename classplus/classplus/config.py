"""
Configuration module for ClassPlus Telegram Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('8672374752:AAFIujzNvd88sMPQUKD-z7w_sJoGQz75tzU')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'classplus_bot.db')

# Download Configuration
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', 'downloads')
MAX_CONCURRENT_DOWNLOADS = 5
CHUNK_SIZE = 8192  # 8KB chunks

# API Configuration
CLASSPLUS_BASE_URL = os.getenv('CLASSPLUS_BASE_URL', 'https://api.classplusapp.com/v2')
CLASSPLUS_API_VERSION = os.getenv('CLASSPLUS_API_VERSION', '52')
CLASSPLUS_REGION = 'IN'
REQUEST_TIMEOUT = 30

# Bot Settings
MAX_COURSES_PER_PAGE = 10
MAX_CONTENT_ITEMS_PER_MESSAGE = 50
DOWNLOAD_PROGRESS_UPDATE_INTERVAL = 5  # seconds

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Session Configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds
TOKEN_REFRESH_INTERVAL = 86400  # 24 hours in seconds

# File Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
ALLOWED_EXTENSIONS = {
    'video': ['.mp4', '.mov', '.avi', '.mkv', '.flv'],
    'pdf': ['.pdf'],
    'archive': ['.zip', '.rar', '.7z'],
}

# Error Messages
ERROR_MESSAGES = {
    'invalid_org': '❌ Invalid organization code. Please check and try again.',
    'invalid_mobile': '❌ Invalid mobile number. Enter 10 digits only.',
    'invalid_otp': '❌ Invalid OTP. Please enter 6 digits.',
    'login_failed': '❌ Login failed. Please try again.',
    'no_courses': '❌ No courses found in your account.',
    'no_content': '❌ No content found in this course.',
    'download_failed': '❌ Download failed. Please retry.',
    'token_expired': '❌ Session expired. Please login again.',
    'network_error': '❌ Network error. Check your connection.',
}

# Success Messages
SUCCESS_MESSAGES = {
    'otp_sent': '✅ OTP sent to {mobile}',
    'login_success': '✅ Login successful!',
    'extraction_complete': '✅ Extraction complete!',
    'download_complete': '✅ Download complete!',
    'logout_success': '✅ Logged out successfully!',
}

# UI Text
UI_TEXTS = {
    'main_menu': """
╔════════════════════════════════╗
║  🎓 CLASSPLUS DOWNLOADER BOT   ║
╠════════════════════════════════╣
║  Download courses from Classplus
║  with ease!
╚════════════════════════════════╝
""",
    'help_text': """
📖 **HOW TO USE THIS BOT:**

1️⃣ **Login**: Click "Login with Classplus" to authenticate
2️⃣ **Select Course**: Choose a course from your list
3️⃣ **Choose Action**: 
   - Extract List: See all videos/PDFs
   - Download All: Download everything
4️⃣ **Done**: Files will be downloaded

⚠️ **NOTES:**
• Large files may take time to download
• Keep the bot running
• Your credentials are secured
• All downloads are automatic

💡 **COMMANDS:**
/start - Main menu
/help - This message
/logout - Clear login
""",
}

# Validate configuration
def validate_config():
    """Validate required configuration"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "❌ TELEGRAM_BOT_TOKEN not set. "
            "Create .env file with: TELEGRAM_BOT_TOKEN=your_token"
        )
    
    # Create download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    return True

# Call validation on import
try:
    validate_config()
except ValueError as e:
    print(str(e))
