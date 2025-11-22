"""
WSGI Entry Point for WhatsApp Bots
Supports both MediGuard AI and Research Paper Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Select which bot to run via BOT_MODE environment variable
# Options: "mediguard" or "research"
# Default: "mediguard"
BOT_MODE = os.getenv("BOT_MODE", "mediguard").lower()

if BOT_MODE == "research":
    # Import Research Paper Bot
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research-paper-bot'))
    from research_bot import app
    print("🤖 Running Research Paper Bot")
else:
    # Import MediGuard AI Bot (default)
    from mediguard_bot import app
    print("🏥 Running MediGuard AI Bot")

# For Gunicorn
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
