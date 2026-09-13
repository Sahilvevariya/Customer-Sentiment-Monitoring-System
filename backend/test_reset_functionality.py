#!/usr/bin/env python3
"""
Test the new email configuration reset and live monitoring functionality
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:5000"

def test_email_config_reset():
    """Test that changing email configuration resets data"""
    print("🧪 Testing Email Configuration Reset Functionality")
    print("=" * 60)
    
    # Test configuration 1
    config1 = {
        "email": "test1@gmail.com",
        "appPassword": "testpassword123",
        "telegramUserId": "123456"
    }
    
    # Test configuration 2 (different email)
    config2 = {
        "email": "test2@gmail.com", 
        "appPassword": "differentpassword456",
        "telegramUserId": "123456"
    }
    
    try:
        # 1. Save first configuration
        print("\n1. Saving first email configuration...")
        response1 = requests.post(f"{BASE_URL}/api/email-config", json=config1)
        if response1.status_code == 201:
            result1 = response1.json()
            print(f"✅ First config saved: {result1.get('message')}")
            print(f"   Data reset: {result1.get('data_reset', 'Not specified')}")
        else:
            print(f"❌ Failed to save first config: {response1.text}")
            return
        
        # 2. Add some test data
        print("\n2. Adding test message data...")
        test_message = {
            "sender": "test@example.com",
            "subject": "Test Message", 
            "body": "This is a test message for angry sentiment",
            "timestamp": datetime.now().isoformat(),
            "user_id": "default_user"
        }
        
        message_response = requests.post(f"{BASE_URL}/message", json=test_message)
        if message_response.status_code == 200:
            print("✅ Test message added")
        else:
            print(f"❌ Failed to add test message: {message_response.text}")
        
        # 3. Check data exists
        print("\n3. Checking data exists...")
        overview_response = requests.get(f"{BASE_URL}/api/emotion-overview")
        if overview_response.status_code == 200:
            overview = overview_response.json()
            total_messages = sum(data.get('count', 0) for data in overview.values() if isinstance(data, dict))
            print(f"✅ Found {total_messages} messages in database")
        else:
            print("❌ Failed to get emotion overview")
            return
        
        # 4. Save second configuration (different email - should trigger reset)
        print("\n4. Saving second email configuration (different email)...")
        response2 = requests.post(f"{BASE_URL}/api/email-config", json=config2)
        if response2.status_code == 201:
            result2 = response2.json()
            print(f"✅ Second config saved: {result2.get('message')}")
            print(f"   Data reset: {result2.get('data_reset', 'Not specified')}")
            
            if result2.get('data_reset'):
                print("🔄 Data should now be reset to zero!")
            else:
                print("❌ Data was not reset - this is unexpected!")
        else:
            print(f"❌ Failed to save second config: {response2.text}")
            return
        
        # 5. Check data is reset
        print("\n5. Verifying data was reset...")
        overview_response2 = requests.get(f"{BASE_URL}/api/emotion-overview")
        if overview_response2.status_code == 200:
            overview2 = overview_response2.json()
            total_messages_after = sum(data.get('count', 0) for data in overview2.values() if isinstance(data, dict))
            print(f"📊 Messages after reset: {total_messages_after}")
            
            if total_messages_after == 0:
                print("✅ SUCCESS: Data was properly reset to zero!")
            else:
                print(f"❌ FAIL: Expected 0 messages, but found {total_messages_after}")
        else:
            print("❌ Failed to verify reset")
        
        print(f"\n🎯 TEST COMPLETE")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Please ensure it's running on localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


def test_live_monitoring_reset():
    """Test the live monitoring with reset functionality"""
    print("\n🧪 Testing Live Monitoring with Reset")
    print("=" * 60)
    
    try:
        # 1. Start live monitoring with reset
        print("1. Starting live monitoring with data reset...")
        response = requests.post(f"{BASE_URL}/api/start-live-monitoring", 
                               json={"user_id": "default_user", "reset_data": True})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Live monitoring started: {result.get('message')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Data reset: {result.get('data_reset')}")
            print(f"   Started at: {result.get('start_timestamp')}")
        else:
            print(f"❌ Failed to start live monitoring: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server")
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_manual_reset():
    """Test the manual reset functionality"""
    print("\n🧪 Testing Manual Data Reset")
    print("=" * 60)
    
    try:
        # Add some test data first
        print("1. Adding test data...")
        test_message = {
            "sender": "manual.test@example.com",
            "subject": "Manual Test",
            "body": "This message should be deleted by manual reset",
            "timestamp": datetime.now().isoformat(),
            "user_id": "default_user"
        }
        
        requests.post(f"{BASE_URL}/message", json=test_message)
        print("✅ Test data added")
        
        # Reset data manually
        print("\n2. Performing manual reset...")
        reset_response = requests.post(f"{BASE_URL}/api/reset-emotion-data",
                                     json={"user_id": "default_user"})
        
        if reset_response.status_code == 200:
            result = reset_response.json()
            print(f"✅ Manual reset completed: {result.get('message')}")
            print(f"   Deleted messages: {result.get('deleted_messages')}")
            print(f"   Reset timestamp: {result.get('reset_timestamp')}")
        else:
            print(f"❌ Manual reset failed: {reset_response.text}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    print("🚀 TESTING EMAIL MONITORING RESET FUNCTIONALITY")
    print("=" * 70)
    
    # Run all tests
    test_email_config_reset()
    time.sleep(2)
    test_live_monitoring_reset() 
    time.sleep(2)
    test_manual_reset()
    
    print(f"\n🏁 ALL TESTS COMPLETED")
    print("=" * 70)
    print("💡 Next steps:")
    print("   1. Test in frontend by changing email/password")
    print("   2. Click 'Live Update' button to start monitoring")
    print("   3. Verify data starts from zero each time")
