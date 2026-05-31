# 🎓 ClassPlus Telegram Bot

A powerful Telegram bot to download courses, videos, and PDFs from ClassPlus with a beautiful UI.

## ✨ Features

- 🔐 **Secure Authentication** - OTP-based login via Classplus
- 📚 **Multi-Course Support** - Browse and manage multiple courses
- 🎬 **Video Downloads** - Download lessons in high quality
- 📄 **PDF Downloads** - Extract and store study materials
- 💾 **Local Database** - SQLite for secure token storage
- 📊 **Progress Tracking** - Real-time download statistics
- 🎨 **Beautiful UI** - Inline keyboards for smooth navigation
- ⚡ **Fast & Reliable** - Optimized for speed and stability
- 🛡️ **Privacy** - All data stored locally, no external storage

## 📋 Requirements

- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- Internet connection
- FFmpeg (optional, for HLS/M3U8 streams)

## 🚀 Installation

### 1. Clone or Download

```bash
cd selection\ away\ bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

On Windows, also install FFmpeg:
```bash
# Using chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

### 3. Configure Bot Token

1. Get your Telegram Bot Token:
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Use `/newbot` command
   - Follow instructions to create a bot
   - Copy the token

2. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and paste your token:
   ```
   TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
   ```

## 🎯 How to Use

### Start the Bot

```bash
python telegram_bot.py
```

You should see:
```
🚀 Bot started! Press Ctrl+C to stop
```

### Using the Bot

1. **Open Telegram** and find your bot
2. **Press `/start`** to see the main menu
3. **Click "Login with Classplus"**
4. **Enter Organization Code** (e.g., BYJUS, VEDANTU)
5. **Enter Mobile Number** (10 digits)
6. **Enter OTP** received on your phone
7. **Select Course** from your list
8. **Choose Action:**
   - 📋 Extract List - See all content
   - ⬇️ Download All - Download everything

### Features Explained

#### Extract List
Shows all videos and PDFs in the course with metadata. Useful for seeing what's available before downloading.

#### Download All
Automatically downloads all course materials:
- Videos are saved as `.mp4`
- PDFs are saved as `.pdf`
- Progress updates in real-time

#### Your Account
- View saved login credentials
- Switch accounts
- View download history
- Check statistics

## 📁 File Structure

```
selection away bot/
├── telegram_bot.py          # Main bot application
├── database.py              # SQLite database layer
├── download_manager.py      # Download handling
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── README.md                # This file
└── classplus_bot.db         # Auto-created database
```

## 🗄️ Database

The bot uses SQLite with three main tables:

### Users Table
Stores login credentials encrypted:
- `user_id` - Telegram user ID
- `token` - ClassPlus API token
- `mobile` - Phone number
- `org_code` - Organization code

### Downloads Table
Tracks all downloads:
- `user_id` - Telegram user ID
- `item_name` - File name
- `item_type` - video/pdf
- `status` - completed/failed
- `downloaded_at` - Timestamp

### Courses Cache
Caches course content:
- `user_id` - Telegram user ID
- `course_id` - ClassPlus course ID
- `course_data` - Cached metadata
- `cached_at` - Cache timestamp

## 🔧 Configuration

Edit these in `telegram_bot.py`:

```python
# API timeout (seconds)
timeout=10

# Maximum courses to show
courses[:10]

# Download chunk size
chunk_size=2*1024*1024
```

## 🐛 Troubleshooting

### "TELEGRAM_BOT_TOKEN not set"
- Check if `.env` file exists
- Verify `TELEGRAM_BOT_TOKEN` is set correctly
- Make sure you're in the correct directory

### "Connection Error"
- Check your internet connection
- Try running: `ping api.classplusapp.com`
- Verify firewall isn't blocking requests

### OTP Not Received
- Check if organization code is correct
- Verify phone number (10 digits)
- Wait a few seconds between retries
- Contact ClassPlus support if persistent

### Download Fails
- Check available disk space
- Verify URL is still valid
- Try extracting list first
- Check file permissions

### "FFmpeg not found"
- Install FFmpeg: `pip install ffmpeg-python`
- Or download from https://ffmpeg.org/download.html

## 🔐 Security

- ✅ Tokens stored locally in encrypted database
- ✅ No credentials sent to third-party services
- ✅ HTTPS for all API calls
- ✅ Device ID randomized per session
- ✅ OTP verified server-side

## 📊 Performance

- Concurrent downloads: Up to 10 streams
- Average download speed: Depends on internet
- Database queries: Optimized with indexes
- Memory usage: ~50-100 MB

## 📝 Logs

Logs are printed to console. For file logging, add:

```python
logging.FileHandler('bot.log')
```

## 🤝 Support

For issues:
1. Check this README
2. Review error messages in console
3. Verify all dependencies are installed
4. Check internet connection
5. Try restarting the bot

## ⚖️ Legal Notice

This bot is for **personal educational use only**. 

**Respect copyright and licensing:**
- Download only content you have access to
- Don't share downloaded materials
- Follow ClassPlus Terms of Service
- Use responsibly

## 🎓 What Can Be Downloaded

✅ Allowed:
- Your own course materials
- Lectures you're enrolled in
- Supplementary content
- PDFs and study notes

❌ Not Allowed:
- Copyright-protected content without permission
- Content from courses you're not enrolled in
- Materials to redistribute
- Anything marked confidential

## 💡 Tips

1. **Fast Downloads**: Download during off-peak hours
2. **Storage**: Check disk space before downloading large courses
3. **Organization**: Create folders for different subjects
4. **Backup**: Backup important files regularly
5. **Updates**: Check for bot updates periodically

## 🔄 Updating the Bot

To update dependencies:
```bash
pip install -r requirements.txt --upgrade
```

To reset database (delete all saved logins):
```bash
rm classplus_bot.db
```

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu |
| `/help` | Help text |
| `/logout` | Clear saved login |

## 🎨 UI Features

- ✅ Beautiful inline keyboards
- ✅ Emoji indicators for file types
- ✅ Progress bars
- ✅ Real-time status updates
- ✅ Responsive to all screen sizes
- ✅ Dark mode friendly

## 🚀 Advanced Usage

### Custom Download Directory

Edit `telegram_bot.py`:
```python
dl_manager = DownloadManager("custom/path/downloads")
```

### Change Database Location

Edit `.env`:
```
DATABASE_PATH=/path/to/custom/db.db
```

### Enable Debug Logging

Edit `telegram_bot.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📞 API Reference

### ClassPlus Endpoints Used

- `GET /v2/orgs/{orgCode}` - Get org details
- `POST /v2/otp/generate` - Send OTP
- `POST /v2/users/verify` - Verify OTP
- `GET /v2/profiles/users/data` - Get courses
- `GET /v2/course/content/get` - Get lesson content
- `GET /cams/uploader/video/jw-signed-url` - Get download URL

## 🎯 Roadmap

Future features:
- [ ] Batch download by date range
- [ ] Direct Telegram file upload support
- [ ] Course search functionality
- [ ] Download speed limiter
- [ ] Playlist support
- [ ] Web dashboard for admin

## 📄 License

Personal use only. Do not redistribute or modify for commercial purposes.

## 🙏 Acknowledgments

- ClassPlus for the excellent platform
- Telegram Bot API
- Open-source libraries used

---

**Made with ❤️ for students**

Last Updated: March 2026
Version: 1.0.0
