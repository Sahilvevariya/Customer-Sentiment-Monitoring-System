#!/usr/bin/env python3
"""
Test email ingestion to diagnose why real emails aren't updating the dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest_email import get_email_config, fetch_and_forward_emails
import requests
from datetime import datetime

def test_email_connection():
    """Test if we can connect to the configured email"""
    print("🧪 Testing Email Connection and Configuration")
    print("=" * 60)
    
    config = get_email_config()
    if not config:
        print("❌ No email configuration found!")
        return False
    
    print(f"✅ Email configuration found:")
    print(f"   📧 Email: {config['email']}")
    print(f"   👤 User ID: {config.get('user_id', 'None')}")
    print(f"   📱 Telegram: {config.get('telegram_user_id', 'Not set')}")
    
    return True

def test_manual_email_fetch():
    """Manually test email fetching"""
    print("\n📧 Testing Manual Email Fetch")
    print("=" * 60)
    
    try:
        print("🔄 Attempting to fetch emails...")
        fetch_and_forward_emails()
        print("✅ Email fetch completed!")
        return True
    except Exception as e:
        print(f"❌ Email fetch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_api():
    """Test that the message API is working"""
    print("\n🧪 Testing Message API")
    print("=" * 60)
    
    test_message = {
        "id": f"test_real_email_{int(datetime.now().timestamp())}",
        "timestamp": datetime.now().isoformat(),
        "source": "email",
        "sender": "test.real.email@example.com",
        "text": "Subject: Test Real Email Processing\n\nThis is a test to see if real email processing works with the dashboard.",
        "emotion": "happy",
        "sentiment": "happy",
        "user_id": "default_user",
        "email_account": "om.agarwal16805@gmail.com"
    }
    
    try:
        response = requests.post("http://127.0.0.1:5000/message", json=test_message)
        if response.status_code in [200, 201]:
            print("✅ Message API is working correctly")
            result = response.json()
            print(f"   📊 Response: {result}")
            return True
        else:
            print(f"❌ Message API failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error calling message API: {e}")
        return False

def check_current_dashboard_data():
    """Check what data is currently in the dashboard"""
    print("\n📊 Checking Current Dashboard Data")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:5000/api/emotion-overview")
        if response.status_code == 200:
            data = response.json()
            total = 0
            print("Current emotion counts:")
            for emotion, info in data.items():
                if isinstance(info, dict) and 'count' in info:
                    count = info['count']
                    total += count
                    print(f"   {emotion}: {count} messages")
            print(f"📈 Total messages: {total}")
            return data
        else:
            print(f"❌ Failed to get dashboard data: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error checking dashboard data: {e}")
        return None

def main():
    print("🔍 DIAGNOSING EMAIL INGESTION ISSUE")
    print("=" * 70)
    print("This will test why real emails aren't updating the dashboard")
    print("=" * 70)
    
    # Test 1: Email configuration
    if not test_email_connection():
        print("\n❌ PROBLEM: Email configuration missing!")
        return
    
    # Test 2: Current dashboard state
    initial_data = check_current_dashboard_data()
    
    # Test 3: Message API
    if not test_message_api():
        print("\n❌ PROBLEM: Message API not working!")
        return
    
    # Test 4: Check if test message appeared
    print("\n⏳ Waiting 3 seconds for processing...")
    import time
    time.sleep(3)
    
    after_test_data = check_current_dashboard_data()
    
    # Test 5: Try to fetch real emails
    print("\n📧 Now testing real email fetch...")
    if test_manual_email_fetch():
        print("\n⏳ Waiting 5 seconds for email processing...")
        time.sleep(5)
        
        final_data = check_current_dashboard_data()
        
        # Compare data
        if initial_data and final_data:
            initial_total = sum(info.get('count', 0) for info in initial_data.values() if isinstance(info, dict))
            final_total = sum(info.get('count', 0) for info in final_data.values() if isinstance(info, dict))
            
            print(f"\n📈 Data comparison:")
            print(f"   Before email fetch: {initial_total} messages")
            print(f"   After email fetch: {final_total} messages")
            
            if final_total > initial_total:
                print("✅ SUCCESS: Real emails were processed!")
            else:
                print("⚠️ No new emails were processed (this might be normal if no unread emails)")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("1. Make sure you have unread emails in black.falcon.x.69@gmail.com")
    print("2. Check that Gmail App Password is correct")
    print("3. Verify IMAP is enabled for the Gmail account")
    print("4. Try clicking 'Start Live' button in the dashboard")

if __name__ == "__main__":
    main()
