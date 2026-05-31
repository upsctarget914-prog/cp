#!/usr/bin/env python3
"""
Run script for ClassPlus Telegram Bot
Execute this to start the bot
"""

import sys
import os
import subprocess

def check_env():
    """Check if setup is complete"""
    if not os.path.exists('.env'):
        print("""
❌ .env file not found!

Run setup first:
  python setup.py
        """)
        return False
    return True

def check_requirements():
    """Check if dependencies are installed"""
    try:
        import telegram
        import requests
        return True
    except ImportError:
        print("""
❌ Dependencies not installed!

Run setup first:
  python setup.py
        """)
        return False

def main():
    print("""
╔═══════════════════════════════════════╗
║  🚀 CLASSPLUS TELEGRAM BOT            ║
╠═══════════════════════════════════════╣
║  Starting bot...
╚═══════════════════════════════════════╝
    """)
    
    if not check_env() or not check_requirements():
        sys.exit(1)
    
    try:
        from telegram_bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n\n✅ Bot stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
