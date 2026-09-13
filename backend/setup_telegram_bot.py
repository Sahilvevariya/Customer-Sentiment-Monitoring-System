#!/usr/bin/env python3
"""
Telegram Bot Setup Script for CustomerSentinel
This script helps you configure your Telegram bot for sentiment alerts.
"""

import requests
import json
import os
from datetime import datetime

def get_bot_token():
    """Interactive bot token input"""
    print("\n🤖 Step 1: Get Your Bot Token")
    print("=" * 40)
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot to create a new bot")
    print("3. Follow the instructions to name your bot")
    print("4. Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    print()
    
    while True:
        token = input("Enter your bot token: ").strip()
        if token and ":" in token and len(token) > 20:
            return token
        else:
            print("❌ Invalid token format. Please enter a valid bot token.")

def get_chat_id(bot_token):
    """Get chat ID by testing the bot"""
    print("\n📱 Step 2: Get Your Chat ID")
    print("=" * 40)
    print("1. Start a chat with your bot (search for your bot username)")
    print("2. Send any message to the bot (like 'Hello')")
    print("3. Press Enter when you've sent a message to the bot")
    print()
    
    input("Press Enter after sending a message to your bot...")
    
    # Get updates to find the chat ID
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    if 'message' in update:
                        chat_id = update['message']['chat']['id']
                        user_name = update['message']['from'].get('first_name', 'Unknown')
                        print(f"✅ Found chat ID: {chat_id} (User: {user_name})")
                        return str(chat_id)
            
            print("❌ No messages found. Please send a message to your bot and try again.")
            return None
        else:
            print(f"❌ Failed to get updates: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting chat ID: {e}")
        return None

def test_bot_connection(bot_token, chat_id):
    """Test the bot connection"""
    print("\n🧪 Step 3: Test Bot Connection")
    print("=" * 40)
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    test_message = f"""
🤖 <b>CustomerSentinel Bot Test</b>

✅ <b>Connection Test Successful!</b>
⏰ <b>Time:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Your Telegram bot is now connected and ready to receive sentiment alerts!
    """
    
    payload = {
        "chat_id": chat_id,
        "text": test_message.strip(),
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Test message sent successfully!")
            print("Check your Telegram to see the test message.")
            return True
        else:
            print(f"❌ Failed to send test message: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

def update_telegram_config(bot_token, chat_id):
    """Update the telegram_alert.py file with the new configuration"""
    print("\n📝 Step 4: Update Configuration")
    print("=" * 40)
    
    config_file = "telegram_alert.py"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the placeholder values
        content = content.replace('BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"', f'BOT_TOKEN = "{bot_token}"')
        content = content.replace('CHAT_ID = "YOUR_CHAT_ID_HERE"', f'CHAT_ID = "{chat_id}"')
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Configuration updated in {config_file}")
        return True
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def create_env_file(bot_token, chat_id):
    """Create a .env file for environment variables"""
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={bot_token}
TELEGRAM_CHAT_ID={chat_id}

# Add other environment variables here
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file for environment variables")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    print("🤖 CustomerSentinel Telegram Bot Setup")
    print("=" * 50)
    print("This script will help you configure your Telegram bot for sentiment alerts.")
    print()
    
    # Step 1: Get bot token
    bot_token = get_bot_token()
    
    # Step 2: Get chat ID
    chat_id = get_chat_id(bot_token)
    if not chat_id:
        print("❌ Could not get chat ID. Please try again.")
        return
    
    # Step 3: Test connection
    if not test_bot_connection(bot_token, chat_id):
        print("❌ Bot connection test failed. Please check your configuration.")
        return
    
    # Step 4: Update configuration
    if not update_telegram_config(bot_token, chat_id):
        print("❌ Failed to update configuration file.")
        return
    
    # Step 5: Create .env file
    create_env_file(bot_token, chat_id)
    
    print("\n🎉 Telegram Bot Setup Complete!")
    print("=" * 50)
    print("✅ Bot token configured")
    print("✅ Chat ID configured")
    print("✅ Connection tested successfully")
    print("✅ Configuration files updated")
    print()
    print("Your Telegram bot is now ready to receive sentiment alerts!")
    print("The bot will automatically send you notifications when:")
    print("• Customer sentiment turns negative")
    print("• Monitoring starts/stops")
    print("• System errors occur")
    print()
    print("To test the integration, run: python telegram_alert.py")

if __name__ == "__main__":
    main()