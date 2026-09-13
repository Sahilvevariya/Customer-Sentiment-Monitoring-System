#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TESTING GUIDE
This script will test all functionality step by step
"""

import requests
import json
from database import DatabaseManager

print("🚀 TESTING EMAIL MONITORING SYSTEM")
print("=" * 60)

# Test 1: Database Connection
print("\n📋 TEST 1: Database Connection")
try:
    db_manager = DatabaseManager()
    db = db_manager.db
    messages = list(db.messages.find({}))
    print(f"✅ Database connected - {len(messages)} messages found")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Test 2: Check if Flask server is running
print("\n📋 TEST 2: Flask Server Status")
try:
    response = requests.get('http://localhost:5000/api/analytics', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("✅ Flask server is running")
        print(f"📊 Current analytics: {data}")
    else:
        print(f"⚠️ Flask server responded with status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Flask server is not running")
    print("💡 To start: Run 'python app.py' in terminal")
except Exception as e:
    print(f"❌ Error checking server: {e}")

# Test 3: Test Reset Functionality
print("\n📋 TEST 3: Reset Functionality Test")
try:
    # Test the reset endpoint
    response = requests.post('http://localhost:5000/api/reset-emotion-data', 
                           json={'user_id': 'test_user'}, timeout=5)
    if response.status_code == 200:
        print("✅ Reset endpoint is working")
    else:
        print(f"⚠️ Reset endpoint status: {response.status_code}")
except Exception as e:
    print(f"❌ Reset test failed: {e}")

# Test 4: Email Configuration Test
print("\n📋 TEST 4: Email Configuration Test")
email_config = {
    'email': 'black.falcon.x.69@gmail.com',
    'password': 'your_app_password_here',  # You need to replace this
    'userId': 'test_user'
}

try:
    response = requests.post('http://localhost:5000/api/email-config', 
                           json=email_config, timeout=5)
    if response.status_code == 200:
        print("✅ Email configuration endpoint working")
    else:
        print(f"⚠️ Email config status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Email config test failed: {e}")

print("\n" + "=" * 60)
print("🎯 MANUAL TESTING STEPS:")
print("1. ✅ Start Flask server: python app.py")
print("2. ✅ Start Frontend: npm run dev (in frontend folder)")
print("3. ✅ Go to localhost:3000 in browser")
print("4. ✅ Test Email Setup page - enter your credentials")
print("5. ✅ Check if data resets automatically")
print("6. ✅ Test Dashboard - click 'Start Live' button")
print("7. ✅ Send yourself a test email")
print("8. ✅ Check if dashboard updates")

print("\n🔧 TROUBLESHOOTING:")
print("• If server won't start: Check if port 5000 is free")
print("• If emails don't process: Check Gmail app password")
print("• If dashboard doesn't update: Check browser console for errors")
print("• If reset doesn't work: Check database connection")
