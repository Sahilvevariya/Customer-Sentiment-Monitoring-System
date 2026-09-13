#!/usr/bin/env python3
"""
Script to set up a test email configuration for default_user
This allows the monitoring system to work without requiring real Gmail credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_database_manager
from datetime import datetime

def setup_test_email_config():
    """Set up a test email configuration for default_user"""
    try:
        db_manager = get_database_manager()
        
        # Test email configuration (you should replace these with real values)
        test_config = {
            "email": "black.falcon.x.69@gmail.com",  # Replace with your actual Gmail
            "app_password": "obzx lclh ozyd aaaa",  # Replace with your actual app password
            "telegram_user_id": "8849699888",  # Replace with your Telegram user ID
            "user_id": "default_user",
            "active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save the configuration
        config_id = db_manager.save_email_config(test_config, "default_user")
        
        print(f"✅ Test email configuration saved with ID: {config_id}")
        print(f"📧 Email: {test_config['email']}")
        print(f"🔑 App Password: {test_config['app_password']}")
        print(f"📱 Telegram User ID: {test_config['telegram_user_id']}")
        print(f"👤 User ID: {test_config['user_id']}")
        
        # Verify the configuration was saved
        saved_config = db_manager.get_email_config("default_user")
        if saved_config:
            print("✅ Configuration verified successfully!")
            return True
        else:
            print("❌ Configuration verification failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up test email config: {e}")
        return False

def main():
    print("🔧 Setting up test email configuration for default_user...")
    print("⚠️  NOTE: This creates a test configuration. For real monitoring, you need:")
    print("   1. A real Gmail address")
    print("   2. A Gmail App Password (generate from Google Account settings)")
    print("   3. Your Telegram User ID (optional)")
    print()
    
    success = setup_test_email_config()
    
    if success:
        print()
        print("🎉 Test configuration setup complete!")
        print("📝 To use real email monitoring, edit the configuration with your actual Gmail credentials.")
        print("🔗 You can also set up email configuration through the web interface at /gmail-setup")
    else:
        print()
        print("❌ Failed to set up test configuration. Please check the error messages above.")

if __name__ == "__main__":
    main() 