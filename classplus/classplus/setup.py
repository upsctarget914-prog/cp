#!/usr/bin/env python3
"""
Setup script for ClassPlus Telegram Bot
Creates initial configuration and installs dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    print("""
╔═══════════════════════════════════════╗
║  🎓 CLASSPLUS TELEGRAM BOT SETUP 🎓   ║
╠═══════════════════════════════════════╣
║  Setting up your bot environment...   ║
╚═══════════════════════════════════════╝
    """)

def check_python():
    """Check Python version"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def install_requirements():
    """Install dependencies"""
    print("\n✓ Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependencies installed")
    except Exception as e:
        print(f"❌ Failed to install: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n✓ Setting up environment...")
    
    if os.path.exists('.env'):
        response = input("⚠️  .env file exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("⏭️  Keeping existing .env")
            return
    
    print("\n🔐 Get your Telegram Bot Token:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Follow instructions to create bot")
    print("4. Copy the token provided\n")
    
    token = input("Paste your TELEGRAM_BOT_TOKEN: ").strip()
    
    if not token:
        print("❌ Token required!")
        sys.exit(1)
    
    env_content = f"""# ClassPlus Telegram Bot Configuration
# Get token from: https://t.me/BotFather

TELEGRAM_BOT_TOKEN={token}

# Database
DATABASE_PATH=classplus_bot.db

# Downloads
DOWNLOAD_DIR=downloads

# Logging
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ .env file created")
    print(f"📝 Token: {token[:10]}...")

def create_directories():
    """Create necessary directories"""
    print("\n✓ Creating directories...")
    
    Path('downloads').mkdir(exist_ok=True)
    print("✅ Downloads directory ready")

def test_imports():
    """Test if all imports work"""
    print("\n✓ Testing imports...")
    try:
        import telegram
        import requests
        from database import Database
        from download_manager import DownloadManager
        from config import TELEGRAM_BOT_TOKEN
        
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    print_header()
    
    try:
        check_python()
        install_requirements()
        create_env_file()
        create_directories()
        
        if test_imports():
            print("""
╔═══════════════════════════════════════╗
║  ✅ SETUP COMPLETE!                   ║
╠═══════════════════════════════════════╣

To start the bot, run:
  python telegram_bot.py

Features:
  ✓ Secure OTP authentication
  ✓ Multi-course support
  ✓ Video & PDF downloads
  ✓ SQLite database
  ✓ Beautiful UI
  ✓ Progress tracking

For help: python telegram_bot.py --help

Questions? Check README.md
╚═══════════════════════════════════════╝
            """)
        else:
            print("❌ Setup partially complete. Check errors above.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
