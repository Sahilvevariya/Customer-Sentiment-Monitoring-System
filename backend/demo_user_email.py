#!/usr/bin/env python3
"""
Quick usage example for the new user-specific email monitoring features
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"

# Example user configurations
EXAMPLE_USERS = [
    {
        "user_id": "support_team",
        "email": "support@company.com",
        "appPassword": "support-app-password",
        "telegramUserId": "123456789",
        "description": "Support Team Email"
    },
    {
        "user_id": "sales_team", 
        "email": "sales@company.com",
        "appPassword": "sales-app-password",
        "telegramUserId": "987654321",
        "description": "Sales Team Email"
    }
]

def setup_user_email_monitoring():
    """Example: Set up email monitoring for multiple users"""
    print("🔧 Setting up user-specific email monitoring...")
    
    for user in EXAMPLE_USERS:
        print(f"\n📧 Configuring {user['description']} ({user['user_id']})...")
        
        # Configure email for user
        config_data = {
            "user_id": user["user_id"],
            "email": user["email"], 
            "appPassword": user["appPassword"],
            "telegramUserId": user["telegramUserId"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/email-config", json=config_data)
            if response.status_code == 201:
                print(f"✅ Configuration saved for {user['user_id']}")
            else:
                print(f"❌ Failed to save config for {user['user_id']}: {response.text}")
        except Exception as e:
            print(f"❌ Error configuring {user['user_id']}: {e}")

def start_monitoring_all_users():
    """Example: Start monitoring all configured users"""
    print("\n🚀 Starting email monitoring for all users...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/start-monitoring")
        if response.status_code == 200:
            print("✅ Monitoring started for all users")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to start monitoring: {response.text}")
    except Exception as e:
        print(f"❌ Error starting monitoring: {e}")

def start_monitoring_specific_user(user_id):
    """Example: Start monitoring for a specific user only"""
    print(f"\n👤 Starting email monitoring for user: {user_id}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/start-monitoring", 
                               json={"user_id": user_id})
        if response.status_code == 200:
            print(f"✅ Monitoring started for user {user_id}")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to start monitoring for {user_id}: {response.text}")
    except Exception as e:
        print(f"❌ Error starting monitoring for {user_id}: {e}")

def fetch_emails_with_temp_credentials():
    """Example: Fetch emails using temporary credentials without saving config"""
    print("\n📩 Fetching emails with temporary credentials...")
    
    temp_credentials = {
        "email": "temp@example.com",  # Replace with actual email
        "password": "temp-app-password"  # Replace with actual password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/fetch-emails-now", 
                               json=temp_credentials)
        if response.status_code == 200:
            print("✅ Email fetch completed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to fetch emails: {response.text}")
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")

def get_user_specific_analytics():
    """Example: Get analytics for specific users"""
    print("\n📊 Getting user-specific analytics...")
    
    for user in EXAMPLE_USERS:
        user_id = user["user_id"]
        print(f"\n📈 Getting emotion trends for {user['description']}...")
        
        try:
            # Get 24-hour emotion trends for this user
            response = requests.get(f"{BASE_URL}/api/emotion-trends", 
                                  params={"user_id": user_id, "hours": 24})
            
            if response.status_code == 200:
                trends_data = response.json()
                trends_count = len(trends_data.get('trends', []))
                print(f"✅ Found {trends_count} hourly data points for {user_id}")
                
                # Calculate total emotions for this user
                total_emotions = {"anger": 0, "confusion": 0, "joy": 0, "neutral": 0}
                for trend in trends_data.get('trends', []):
                    for emotion in total_emotions:
                        total_emotions[emotion] += trend.get(emotion, 0)
                
                print(f"📊 Total emotions for {user_id}: {total_emotions}")
            else:
                print(f"❌ Failed to get trends for {user_id}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting analytics for {user_id}: {e}")

def list_all_configurations():
    """Example: List all email configurations"""
    print("\n📋 Listing all email configurations...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/list-email-configs")
        if response.status_code == 200:
            configs_data = response.json()
            print(f"✅ Found {configs_data.get('count', 0)} configurations:")
            
            for i, config in enumerate(configs_data.get('configs', []), 1):
                user_id = config.get('user_id', 'Global')
                email = config.get('email', 'Unknown')
                created = config.get('created_at', 'Unknown')
                print(f"  {i}. {email} (User: {user_id}) - Created: {created}")
        else:
            print(f"❌ Failed to list configurations: {response.text}")
    except Exception as e:
        print(f"❌ Error listing configurations: {e}")

def test_user_email_connections():
    """Example: Test email connections for all configured users"""
    print("\n🔌 Testing email connections...")
    
    for user in EXAMPLE_USERS:
        user_id = user["user_id"]
        print(f"\n🧪 Testing connection for {user['description']}...")
        
        try:
            response = requests.get(f"{BASE_URL}/api/test-email-config", 
                                  params={"user_id": user_id})
            
            if response.status_code == 200:
                print(f"✅ Connection successful for {user_id}")
            else:
                print(f"❌ Connection failed for {user_id}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing connection for {user_id}: {e}")

def demonstrate_real_time_monitoring():
    """Example: Demonstrate real-time monitoring workflow"""
    print("\n🔄 Demonstrating real-time monitoring workflow...")
    
    print("1. Setting up configurations...")
    setup_user_email_monitoring()
    time.sleep(2)
    
    print("\n2. Testing connections...")
    test_user_email_connections()
    time.sleep(2)
    
    print("\n3. Listing all configurations...")
    list_all_configurations()
    time.sleep(2)
    
    print("\n4. Fetching emails for specific user...")
    if EXAMPLE_USERS:
        user_id = EXAMPLE_USERS[0]["user_id"]
        try:
            response = requests.post(f"{BASE_URL}/api/fetch-emails-now", 
                                   json={"user_id": user_id})
            if response.status_code == 200:
                print(f"✅ Email fetch completed for {user_id}")
            else:
                print(f"❌ Email fetch failed for {user_id}")
        except Exception as e:
            print(f"❌ Error fetching emails for {user_id}: {e}")
    
    time.sleep(2)
    
    print("\n5. Getting user-specific analytics...")
    get_user_specific_analytics()
    
    print("\n6. Starting continuous monitoring...")
    start_monitoring_all_users()

def main():
    """Main demonstration function"""
    print("🚀 User-Specific Email Monitoring Demo")
    print("=" * 50)
    
    print("\n⚠️ IMPORTANT: Update EXAMPLE_USERS with your actual email credentials before running!")
    print("⚠️ Make sure the Flask server is running on http://127.0.0.1:5000")
    
    # Check server connectivity
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server responded with error")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the Flask app first.")
        return
    
    print("\n" + "=" * 50)
    
    # Run demonstration
    demonstrate_real_time_monitoring()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\nNext steps:")
    print("1. Update the EXAMPLE_USERS with your actual credentials")
    print("2. Run individual functions as needed")
    print("3. Use the API endpoints in your frontend application")
    print("4. Monitor the console logs for real-time email processing")

if __name__ == "__main__":
    main()
