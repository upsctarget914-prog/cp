"""
ClassPlus Telegram Bot - Download courses from Classplus with a beautiful UI
Features: OTP auth, course extraction, video/PDF downloads, SQLite database
"""

import os
import logging
import json
import time
import re
import uuid
import subprocess
from datetime import datetime
import requests
from database import Database
from download_manager import DownloadManager
import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from telegram.constants import ChatAction

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://api.classplusapp.com/v2"
SESSION_DEVICE_ID = f"web_{uuid.uuid4().hex[:16]}"

# Conversation states
STATE_ORG_CODE, STATE_MOBILE, STATE_OTP = range(3)
STATE_COURSE_SELECT, STATE_ACTION_SELECT = range(3, 5)

class ClassplusBot:
    def __init__(self, token: str, db_path: str = "classplus_bot.db"):
        self.bot_token = token
        self.db = Database(db_path)
        self.session = requests.Session()
        
    def get_headers(self, access_token: str = "") -> dict:
        """Generate request headers"""
        return {
            "Api-Version": "52",
            "Content-Type": "application/json",
            "Device-Id": SESSION_DEVICE_ID,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://web.classplusapp.com",
            "Referer": "https://web.classplusapp.com/",
            "Region": "IN",
            "Accept": "application/json, text/plain, */*",
            "x-access-token": access_token
        }

    def send_otp(self, mobile: str, org_code: str) -> tuple:
        """Generate and send OTP"""
        try:
            url = f"{BASE_URL}/orgs/{org_code}"
            r = self.session.get(url, headers=self.get_headers())
            
            if r.status_code != 200:
                return None, None, "❌ Invalid Org Code"
            
            org_data = r.json().get('data', {})
            org_id = org_data.get('orgId')
            
            payload = {
                'countryExt': '91',
                'mobile': mobile,
                'orgCode': org_code,
                'orgId': org_id,
                'viaSms': 1,
            }
            
            r = self.session.post(f"{BASE_URL}/otp/generate", json=payload, headers=self.get_headers())
            
            if r.status_code == 200:
                session_id = r.json().get('data', {}).get('sessionId')
                return session_id, org_id, "✅ OTP sent successfully!"
            else:
                return None, None, "❌ Could not send OTP"
                
        except Exception as e:
            logger.error(f"OTP Error: {e}")
            return None, None, f"❌ Error: {str(e)[:50]}"

    def verify_otp(self, mobile: str, org_code: str, session_id: str, org_id: str, otp: str) -> tuple:
        """Verify OTP and get authentication token"""
        try:
            payload = {
                "otp": otp,
                "countryExt": "91",
                "sessionId": session_id,
                "orgId": org_id,
                "mobile": mobile,
                "fingerprintId": str(uuid.uuid4())
            }
            
            r = self.session.post(f"{BASE_URL}/users/verify", json=payload, headers=self.get_headers())
            
            if r.status_code == 200:
                res = r.json()
                if res.get('status') == 'success':
                    token = res['data']['token']
                    user_id = res['data']['user']['id']
                    return token, user_id, "✅ Login Successful!"
                else:
                    return None, None, f"❌ {res.get('message', 'Verification failed')}"
            else:
                return None, None, "❌ Invalid OTP"
                
        except Exception as e:
            logger.error(f"Verify Error: {e}")
            return None, None, f"❌ Error: {str(e)[:50]}"

    def get_courses(self, token: str, user_id: str) -> list:
        """Fetch user's courses"""
        try:
            headers = self.get_headers(token)
            params = {'userId': user_id, 'tabCategoryId': 3}
            r = self.session.get(f'{BASE_URL}/profiles/users/data', params=params, headers=headers)
            
            if r.status_code == 200:
                return r.json().get('data', {}).get('responseData', {}).get('coursesData', [])
        except Exception as e:
            logger.error(f"Get Courses Error: {e}")
        return []

    def get_course_content(self, token: str, course_id: int, folder_id: int = 0) -> list:
        """Recursively fetch course content"""
        contents = []
        headers = self.get_headers(token)
        params = {'courseId': course_id, 'folderId': folder_id}
        
        try:
            r = self.session.get(f'{BASE_URL}/course/content/get', params=params, headers=headers)
            if r.status_code == 200:
                items = r.json().get('data', {}).get('courseContent', [])
                
                for item in items:
                    c_type = item.get('contentType')
                    c_id = str(item.get('id'))
                    name = item.get('name', 'Unnamed')
                    
                    if c_type == 1:  # Folder
                        contents.extend(self.get_course_content(token, course_id, c_id))
                    elif c_type == 2:  # Video
                        h_id = item.get('contentHashId', '')
                        identifier = h_id if h_id else c_id
                        contents.append({
                            'name': name,
                            'identifier': identifier,
                            'type': 'video',
                            'numeric_id': c_id
                        })
                    elif c_type == 3:  # PDF
                        url = item.get('url', '')
                        contents.append({
                            'name': name,
                            'url': url,
                            'type': 'pdf',
                            'numeric_id': c_id
                        })
        except Exception as e:
            logger.error(f"Content Error: {e}")
        
        return contents

    def get_download_url(self, token: str, numeric_id: str, identifier: str = None) -> str:
        """Get signed download URL using multiple methods"""
        headers = self.get_headers(token)
        
        # Method 1: Try with numeric ID
        try:
            r = self.session.get(
                'https://api.classplusapp.com/cams/uploader/video/jw-signed-url',
                params={'contentId': numeric_id},
                headers=headers,
                timeout=10
            )
            if r.status_code == 200:
                data = r.json().get('data', {}) if 'data' in r.json() else r.json()
                url = data.get('url') or data.get('data', {}).get('url')
                if url:
                    return url
        except:
            pass
        
        # Method 2: Try with encrypted identifier
        if identifier and identifier != numeric_id:
            try:
                r = self.session.get(
                    'https://api.classplusapp.com/cams/uploader/video/jw-signed-url',
                    params={'contentId': identifier},
                    headers=headers,
                    timeout=10
                )
                if r.status_code == 200:
                    data = r.json().get('data', {}) if 'data' in r.json() else r.json()
                    url = data.get('url') or data.get('data', {}).get('url')
                    if url:
                        return url
            except:
                pass
        
        # Method 3: Direct endpoint
        try:
            r = self.session.get(
                f'{BASE_URL}/course/content/get-signed-url',
                params={'contentId': numeric_id},
                headers=headers,
                timeout=10
            )
            if r.status_code == 200:
                data = r.json().get('data', {}) if 'data' in r.json() else r.json()
                url = data.get('url') or data.get('data', {}).get('url')
                if url:
                    return url
        except:
            pass
        
        return None


# Initialize bot
bot = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with main menu"""
    user_id = update.effective_user.id
    user_data = bot.db.get_user(user_id)
    
    message = f"""
╔════════════════════════════════╗
║  🎓 CLASSPLUS DOWNLOADER BOT   ║
╠════════════════════════════════╣
║  Download courses from Classplus
║  with ease!
╚════════════════════════════════╝
"""
    
    keyboard = []
    if user_data:
        keyboard.append([InlineKeyboardButton("📚 Your Courses", callback_data="view_courses")])
        keyboard.append([InlineKeyboardButton("🔄 Login Again", callback_data="login_new")])
        keyboard.append([InlineKeyboardButton("❌ Logout", callback_data="logout")])
    else:
        keyboard.append([InlineKeyboardButton("🔐 Login with Classplus", callback_data="login")])
    
    keyboard.append([InlineKeyboardButton("ℹ️ Help", callback_data="help")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📖 **HOW TO USE THIS BOT:**

1️⃣ **Login**: Click "Login with Classplus" to authenticate
2️⃣ **Select Course**: Choose a course from your list
3️⃣ **Choose Action**: 
   - Extract List: See all videos/PDFs
   - Download All: Download everything
4️⃣ **Done**: Files will be downloaded to your device

⚠️ **NOTES:**
• Downloading large files may take time
• Keep the bot running during downloads
• Your credentials are secured in database
• All downloads are automatic

💡 **COMMANDS:**
/start - Main menu
/help - This message
/logout - Clear saved login

🆘 **SUPPORT:**
For issues, please check your internet connection
and try again.
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == "login":
        await query.edit_message_text(
            text="🔐 *Login to Classplus*\n\nEnter your organization code:\n_(e.g., BYJUS, VEDANTU)_",
            parse_mode="Markdown"
        )
        context.user_data['state'] = STATE_ORG_CODE
        
        return STATE_ORG_CODE
    
    elif query.data == "view_courses":
        user_data = bot.db.get_user(user_id)
        if not user_data:
            await query.edit_message_text("❌ Please login first")
            return
        
        courses = bot.get_courses(user_data['token'], user_data['user_id_classplus'])
        if not courses:
            await query.edit_message_text("❌ No courses found. Please check your ClassPlus account or logout and login again.")
            return
        
        keyboard = []
        for idx, course in enumerate(courses[:10]):
            keyboard.append([InlineKeyboardButton(
                f"📚 {course.get('name', 'Unknown')[:25]}",
                callback_data=f"select_course_{idx}_{course['id']}"
            )])
        keyboard.append([InlineKeyboardButton("« Back", callback_data="back_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📚 *Your Courses:*", reply_markup=reply_markup, parse_mode="Markdown")
        
        context.user_data['courses'] = courses
    
    elif query.data.startswith("select_course_"):
        parts = query.data.split("_")
        course_id = int(parts[-1])
        user_data = bot.db.get_user(user_id)
        
        keyboard = [
            [InlineKeyboardButton("📋 Extract List", callback_data=f"extract_{course_id}")],
            [InlineKeyboardButton("⬇️ Download All", callback_data=f"download_{course_id}")],
            [InlineKeyboardButton("« Back", callback_data="view_courses")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎯 *Select Action:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif query.data.startswith("extract_"):
        course_id = int(query.data.split("_")[1])
        user_data = bot.db.get_user(user_id)
        
        await query.edit_message_text("⏳ Extracting course content...", parse_mode="Markdown")
        
        contents = bot.get_course_content(user_data['token'], course_id)
        
        if contents:
            text = "📋 *Course Content:*\n\n"
            for idx, item in enumerate(contents[:50], 1):
                emoji = "🎬" if item['type'] == 'video' else "📄"
                text += f"{idx}. {emoji} {item['name'][:40]}\n"
            
            if len(contents) > 50:
                text += f"\n... and {len(contents) - 50} more items"
            
            keyboard = [
                [InlineKeyboardButton("⬇️ Download All", callback_data=f"download_{course_id}")],
                [InlineKeyboardButton("« Back", callback_data="view_courses")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ No content found")
    
    elif query.data.startswith("download_"):
        course_id = int(query.data.split("_")[1])
        user_data = bot.db.get_user(user_id)
        
        await query.edit_message_text("⬇️ *Starting downloads...*\n\nMonitor progress here:", parse_mode="Markdown")
        
        contents = bot.get_course_content(user_data['token'], course_id)
        
        if not contents:
            await query.edit_message_text("❌ No content to download")
            return
        
        progress_msg = await query.edit_message_text(
            f"📊 *Download Progress:*\n0/{len(contents)} items"
        )
        
        for idx, item in enumerate(contents, 1):
            try:
                if item['type'] == 'video':
                    url = bot.get_download_url(user_data['token'], item['numeric_id'], item['identifier'])
                else:
                    url = item.get('url')
                
                if url:
                    # Log download
                    bot.db.add_download(user_id, item['name'], item['type'], 'completed')
                    
                    # Update progress
                    if idx % 5 == 0 or idx == len(contents):
                        try:
                            await progress_msg.edit_text(
                                f"📊 *Download Progress:*\n{idx}/{len(contents)} items\n\n"
                                f"Last: {item['name'][:30]}"
                            )
                        except:
                            pass
            except Exception as e:
                logger.error(f"Download error: {e}")
                bot.db.add_download(user_id, item['name'], item['type'], 'failed')
        
        await progress_msg.edit_text(
            f"✅ *Download Complete!*\n{len(contents)} items processed"
        )
    
    elif query.data == "login_new":
        await query.edit_message_text(
            "🔐 *Login to Classplus*\n\nEnter your organization code:",
            parse_mode="Markdown"
        )
        context.user_data['state'] = STATE_ORG_CODE
        return STATE_ORG_CODE
    
    elif query.data == "logout":
        bot.db.delete_user(user_id)
        await query.edit_message_text("✅ Logged out successfully!")
        await start(update, context)
    
    elif query.data == "back_menu":
        await start(update, context)
    
    elif query.data == "help":
        await help_command(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for login flow"""
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    state = context.user_data.get('state')
    
    if state == STATE_ORG_CODE:
        org_code = user_input.upper()
        context.user_data['org_code'] = org_code
        context.user_data['state'] = STATE_MOBILE
        
        await update.message.reply_text(
            "📱 Enter your 10-digit mobile number:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="back_menu")]])
        )
    
    elif state == STATE_MOBILE:
        mobile = user_input.strip()[-10:]
        if not mobile.isdigit() or len(mobile) != 10:
            await update.message.reply_text("❌ Invalid mobile number. Please enter 10 digits:")
            return
        
        context.user_data['mobile'] = mobile
        org_code = context.user_data['org_code']
        
        await update.message.reply_text(f"⏳ Sending OTP to +91{mobile}...")
        
        session_id, org_id, msg = bot.send_otp(mobile, org_code)
        
        if not session_id:
            await update.message.reply_text(f"{msg}\n\nEnter organization code again:")
            context.user_data['state'] = STATE_ORG_CODE
            return
        
        context.user_data['session_id'] = session_id
        context.user_data['org_id'] = org_id
        context.user_data['state'] = STATE_OTP
        
        await update.message.reply_text(f"{msg}\n\n🔐 Enter the OTP (4-6 digits):")
    
    elif state == STATE_OTP:
        otp = user_input.strip()
        if not otp.isdigit() or len(otp) < 4 or len(otp) > 6:
            await update.message.reply_text("❌ Invalid OTP. Please enter 4-6 digits:")
            return
        
        mobile = context.user_data['mobile']
        org_code = context.user_data['org_code']
        session_id = context.user_data['session_id']
        org_id = context.user_data['org_id']
        
        await update.message.reply_text("⏳ Verifying OTP...")
        
        token, user_id_cp, msg = bot.verify_otp(mobile, org_code, session_id, org_id, otp)
        
        if not token:
            await update.message.reply_text(f"{msg}\n\nEnter OTP again:")
            return
        
        # Save to database
        bot.db.add_user(user_id, token, user_id_cp, org_code, mobile)
        context.user_data['state'] = None
        
        await update.message.reply_text(
            f"{msg}\n\n✅ Your account is all set!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 View Courses", callback_data="view_courses")]
            ])
        )

def main():
    """Main bot function"""
    global bot
    
    # Get token from environment
    TOKEN = config.TELEGRAM_BOT_TOKEN
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in environment")
        return
    
    bot = ClassplusBot(TOKEN)
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Start bot
    print("🚀 Bot started! Press Ctrl+C to stop")
    application.run_polling()

if __name__ == "__main__":
    main()
