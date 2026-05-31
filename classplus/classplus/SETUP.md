# 📋 COMPLETE SETUP GUIDE

Complete setup instructions for all platforms.

## 📊 Project Structure

Your bot now has this structure:

```
selection away bot/
├── telegram_bot.py           # Main bot code (350+ lines)
├── database.py               # SQLite layer with 4 tables
├── download_manager.py       # Download handler with progress
├── config.py                 # Configuration management
├── setup.py                  # Automated setup script
├── run.py                    # Bot launcher
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
├── README.md                 # Detailed documentation
├── QUICKSTART.md             # Windows quick start
├── start_bot.bat             # Windows batch launcher
├── start_bot.ps1             # Windows PowerShell launcher
└── SETUP.md                  # This file
```

## 🎯 Key Features

### Authentication System
- ✅ OTP-based login matching ClassPlus
- ✅ Secure token storage in SQLite
- ✅ Session management
- ✅ Auto-refresh capability

### User Interface
- ✅ Beautiful inline keyboards with emojis
- ✅ Real-time progress tracking
- ✅ Course browser with pagination
- ✅ Responsive design for all devices

### Database (SQLite)
- ✅ Users table: credentials & settings
- ✅ Downloads table: history & tracking
- ✅ Courses table: caching system
- ✅ Automatic cleanup old data

### Download Management
- ✅ Video downloading (MP4)
- ✅ PDF extraction
- ✅ HLS/M3U8 stream support
- ✅ Progress notifications
- ✅ Concurrent downloads
- ✅ Resume capability

### Error Handling
- ✅ Network error recovery
- ✅ Invalid credential handling
- ✅ Timeout management
- ✅ Graceful degradation

## 🖥️ Platform-Specific Setup

### Windows 10/11

#### Option 1: Automated (Recommended)

```powershell
# Download Python first: https://www.python.org/downloads/

# Method A: Batch file (easiest)
start_bot.bat

# Method B: PowerShell
.\start_bot.ps1

# Method C: Command Prompt
python setup.py
python run.py
```

#### Option 2: Manual

```powershell
# Install Python from https://www.python.org/downloads/
# During installation, CHECK "Add Python to PATH"

# Open PowerShell in bot folder and run:
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with your token:
# TELEGRAM_BOT_TOKEN=your_token_here

# Start bot:
python run.py
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and FFmpeg
brew install python@3.10 ffmpeg

# Navigate to bot folder
cd path/to/selection\ away\ bot

# Install dependencies
pip install -r requirements.txt

# Setup
python setup.py

# Start bot
python run.py
```

### Linux (Ubuntu/Debian)

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv ffmpeg

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Setup
python setup.py

# Start bot
python run.py
```

### Linux (Fedora/RHEL)

```bash
# Install dependencies
sudo dnf install python3-pip ffmpeg

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Setup
python setup.py

# Start bot
python run.py
```

## 🔐 Bot Token Setup

### get from BotFather

1. **Open Telegram** 
2. **Search** for `@BotFather`
3. **Send** `/newbot`
4. **Follow prompts**:
   - Name: "ClassPlus Downloader"
   - Username: "my_classplus_bot" (must be unique)
5. **Copy token** (example: `123456789:ABCDefGHIJKlmnopqrsTUVwxyz`)

### Add to .env

Create file `.env` in bot folder:

```
TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIJKlmnopqrsTUVwxyz
DATABASE_PATH=classplus_bot.db
DOWNLOAD_DIR=downloads
LOG_LEVEL=INFO
```

## ✅ Verification

After setup, verify everything works:

```bash
# Test imports
python -c "from telegram import Update; print('✅ Telegram OK')"
python -c "import requests; print('✅ Requests OK')"
python -c "from database import Database; print('✅ Database OK')"

# Test database
python -c "from database import Database; db = Database(); print('✅ DB created')"

# Start bot
python run.py
```

Expected output:
```
🚀 Bot started! Press Ctrl+C to stop
```

## 🚀 Usage

### Start Bot

```bash
# Simple start
python run.py

# Or using setup script
python setup.py     # First time only
python run.py       # Every time

# Windows batch
start_bot.bat

# Windows PowerShell
.\start_bot.ps1
```

### Interact with Bot

1. Open Telegram
2. Search your bot username
3. Click **START**
4. Login with ClassPlus credentials
5. Select course
6. Download content

## 📊 Database Schema

### users table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    token TEXT NOT NULL,
    user_id_classplus INTEGER,
    org_code TEXT,
    mobile TEXT,
    created_at TIMESTAMP,
    last_login TIMESTAMP
)
```

### downloads table
```sql
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    item_name TEXT,
    item_type TEXT,
    status TEXT,
    downloaded_at TIMESTAMP
)
```

### courses_cache table
```sql
CREATE TABLE courses_cache (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    course_id INTEGER,
    course_name TEXT,
    course_data TEXT,
    cached_at TIMESTAMP
)
```

## 🔧 Configuration

Edit `config.py` or `.env`:

```ini
# Bot token (from BotFather)
TELEGRAM_BOT_TOKEN=xxx

# Database file location
DATABASE_PATH=classplus_bot.db

# Download directory
DOWNLOAD_DIR=downloads

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# API timeout (seconds)
REQUEST_TIMEOUT=30

# Items per page
MAX_COURSES_PER_PAGE=10
```

## 🐛 Common Issues & Solutions

### "ModuleNotFoundError: No module named 'telegram'"
```bash
pip install python-telegram-bot
```

### "TELEGRAM_BOT_TOKEN not set"
- Create `.env` file
- Add: `TELEGRAM_BOT_TOKEN=your_token`

### "Connection Error"
- Check internet connection
- Check firewall settings
- Try VPN if blocked

### "FFmpeg not found"
- Install FFmpeg:
  - Windows: `choco install ffmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### "Database locked"
- Close other instances of bot
- Delete `.db-journal` file if exists
- Restart bot

### "OTP not received"
- Check mobile number (10 digits)
- Check org code spelling
- Wait 30 seconds before retry

## 📈 Performance Tips

1. **First Time Setup**: Takes 2-3 minutes
2. **Bot Start**: Takes 5-10 seconds
3. **Course Loading**: 1-5 seconds per course
4. **Download Speed**: Depends on your internet
5. **Database Size**: ~1MB per 1000 downloads

## 🔒 Security

- ✅ Tokens stored locally
- ✅ Database is plaintext (change if needed)
- ✅ HTTPS for all API calls
- ✅ OTP verified server-side
- ✅ No external storage

For additional security:
```bash
# Encrypt database (requires cryptography package)
pip install cryptography

# Set file permissions (Linux/Mac)
chmod 600 classplus_bot.db
chmod 600 .env
```

## 🔄 Updating

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Reset database (delete all saved logins)
rm classplus_bot.db

# Check for code updates
# Check GitHub or project page
```

## 💾 Backup

Backup important files:

```bash
# Backup database
cp classplus_bot.db classplus_bot.db.backup

# Backup configuration
cp .env .env.backup

# Backup downloads
cp -r downloads downloads.backup
```

## 🆘 Getting Help

Check these in order:
1. **README.md** - Detailed documentation
2. **QUICKSTART.md** - Windows quick start
3. **Console output** - Error messages
4. **Config.py** - Settings explanation
5. **Comments in code** - Code documentation

## 📞 Support Resources

- Telegram: [@BotFather](https://t.me/botfather) for bot issues
- Python: https://www.python.org/
- python-telegram-bot: https://python-telegram-bot.readthedocs.io/

## 📝 Notes

- Keep bot running while using
- Don't share your bot token
- Check disk space before large downloads
- Monitor console for errors
- Restart bot if unresponsive

## ✨ Next Steps

1. ✅ Run `setup.py`
2. ✅ Get bot token from BotFather
3. ✅ Add token to `.env`
4. ✅ Run `run.py`
5. ✅ Open Telegram and test bot
6. ✅ Login with ClassPlus
7. ✅ Download courses

---

**Happy Learning! 📚**

Last Updated: March 2026
