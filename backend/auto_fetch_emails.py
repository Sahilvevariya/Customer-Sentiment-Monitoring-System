#!/usr/bin/env python3
"""
Auto email fetcher - runs every 30 seconds to fetch new emails
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

def fetch_emails_periodically():
    """Continuously fetch emails every 30 seconds"""
    print("🔄 Starting automatic email fetching...")
    print("This will fetch emails every 30 seconds. Press Ctrl+C to stop.")
    
    fetch_count = 0
    
    try:
        while True:
            fetch_count += 1
            print(f"\n📧 Fetch cycle #{fetch_count} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                # Try to fetch emails using stored configuration first
                response = requests.post(f"{BASE_URL}/api/start-monitoring", 
                                       json={}, 
                                       timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Monitoring triggered: {result.get('message', 'Success')}")
                else:
                    print(f"❌ Failed to trigger monitoring: {response.status_code}")
                    print(f"   Response: {response.text}")
            
            except requests.exceptions.Timeout:
                print("⏰ Request timed out - continuing...")
            except Exception as e:
                print(f"❌ Error fetching emails: {e}")
            
            # Wait 30 seconds before next fetch
            print("⏰ Waiting 30 seconds before next fetch...")
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n🛑 Email fetching stopped by user")
        print("📊 Final fetch count:", fetch_count)

def test_api_endpoints():
    """Test all API endpoints to make sure they're working"""
    print("🧪 Testing API endpoints...")
    
    endpoints = [
        ("GET", "/api/email-config", "Email Config"),
        ("GET", "/api/emotion-trends", "Emotion Trends"),
        ("GET", "/api/emotion-overview", "Emotion Overview"),
        ("GET", "/api/list-email-configs", "List Email Configs"),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            status = "✅ OK" if response.status_code < 400 else "❌ ERROR"
            print(f"{status} {name}: {response.status_code}")
            
            if response.status_code >= 400:
                print(f"   Error: {response.text[:100]}")
        
        except Exception as e:
            print(f"❌ ERROR {name}: {e}")

if __name__ == "__main__":
    print("🚀 Auto Email Fetcher")
    print("=" * 50)
    
    # Test endpoints first
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    
    # Start automatic fetching
    fetch_emails_periodically()
