#!/usr/bin/env python3
"""
Test script for user-specific email fetching functionality
"""
import json
import requests
import time
from datetime import datetime

# Base API URL
BASE_URL = "http://127.0.0.1:5000"

def test_user_email_config():
    """Test adding a user-specific email configuration"""
    print("🧪 Testing user-specific email configuration...")
    
    # Test data
    test_user_id = "test_user_123"
    test_config = {
        "user_id": test_user_id,
        "email": "user@example.com",  # Replace with actual email
        "appPassword": "your_app_password",  # Replace with actual app password
        "telegramUserId": "123456789"
    }
    
    try:
        # 1. Save email configuration for user
        print(f"📧 Saving email config for user {test_user_id}...")
        response = requests.post(f"{BASE_URL}/api/email-config", json=test_config)
        
        if response.status_code == 201:
            print("✅ Email configuration saved successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to save config: {response.status_code}")
            print(f"Error: {response.text}")
            return False
        
        # 2. Retrieve email configuration for user
        print(f"📖 Retrieving email config for user {test_user_id}...")
        response = requests.get(f"{BASE_URL}/api/email-config", params={"user_id": test_user_id})
        
        if response.status_code == 200:
            print("✅ Email configuration retrieved successfully!")
            config_data = response.json()
            print(f"Config: {json.dumps(config_data, indent=2)}")
        else:
            print(f"❌ Failed to retrieve config: {response.status_code}")
            return False
        
        # 3. Test email connection for user
        print(f"🔌 Testing email connection for user {test_user_id}...")
        response = requests.get(f"{BASE_URL}/api/test-email-config", params={"user_id": test_user_id})
        
        if response.status_code == 200:
            print("✅ Email connection test successful!")
            print(f"Result: {response.json()}")
        else:
            print(f"⚠️ Email connection test failed: {response.status_code}")
            print(f"Error: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def test_fetch_emails_with_credentials():
    """Test fetching emails with provided credentials"""
    print("🧪 Testing email fetch with provided credentials...")
    
    # Test data - Replace with actual credentials
    test_credentials = {
        "email": "your-email@gmail.com",  # Replace with actual email
        "password": "your_app_password"   # Replace with actual app password
    }
    
    try:
        print(f"📧 Fetching emails for {test_credentials['email']}...")
        response = requests.post(f"{BASE_URL}/api/fetch-emails-now", json=test_credentials)
        
        if response.status_code == 200:
            print("✅ Email fetch completed successfully!")
            print(f"Result: {response.json()}")
            return True
        else:
            print(f"❌ Email fetch failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def test_emotion_trends_with_user_filter():
    """Test emotion trends endpoint with user filtering"""
    print("🧪 Testing emotion trends with user filter...")
    
    test_user_id = "test_user_123"
    
    try:
        # Test with user filter
        print(f"📊 Getting emotion trends for user {test_user_id}...")
        response = requests.get(f"{BASE_URL}/api/emotion-trends", params={
            "user_id": test_user_id,
            "hours": 24
        })
        
        if response.status_code == 200:
            print("✅ Emotion trends retrieved successfully!")
            trends_data = response.json()
            print(f"Trends count: {len(trends_data.get('trends', []))}")
            print(f"Time range: {trends_data.get('time_range_hours')} hours")
            if trends_data.get('user_id'):
                print(f"User ID: {trends_data.get('user_id')}")
        else:
            print(f"❌ Failed to get emotion trends: {response.status_code}")
            print(f"Error: {response.text}")
        
        # Test without user filter (global trends)
        print("📊 Getting global emotion trends...")
        response = requests.get(f"{BASE_URL}/api/emotion-trends", params={"hours": 6})
        
        if response.status_code == 200:
            print("✅ Global emotion trends retrieved successfully!")
            trends_data = response.json()
            print(f"Global trends count: {len(trends_data.get('trends', []))}")
        else:
            print(f"⚠️ Failed to get global emotion trends: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def test_list_email_configs():
    """Test listing all email configurations"""
    print("🧪 Testing list email configurations...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/list-email-configs")
        
        if response.status_code == 200:
            print("✅ Email configurations listed successfully!")
            configs_data = response.json()
            print(f"Found {configs_data.get('count', 0)} email configurations")
            
            for i, config in enumerate(configs_data.get('configs', []), 1):
                print(f"  {i}. Email: {config.get('email')}, User ID: {config.get('user_id', 'Global')}")
        else:
            print(f"❌ Failed to list email configurations: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting user-specific email functionality tests...")
    print("=" * 60)
    
    # Wait for server to be ready
    print("⏰ Waiting for server to be ready...")
    time.sleep(2)
    
    try:
        # Test server connectivity
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the Flask app first.")
            return
        print("✅ Server is running!")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the Flask app first.")
        return
    
    print("\n" + "=" * 60)
    
    # Run tests
    tests = [
        ("User Email Configuration", test_user_email_config),
        ("Email Fetch with Credentials", test_fetch_emails_with_credentials),
        ("Emotion Trends with User Filter", test_emotion_trends_with_user_filter),
        ("List Email Configurations", test_list_email_configs)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"Result: {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"❌ FAILED with exception: {e}")
            results.append((test_name, False))
        
        print("-" * 40)
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
