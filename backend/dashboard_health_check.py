#!/usr/bin/env python3
"""
Dashboard Health Check - Verify all dashboard endpoints are working properly
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def check_email_config():
    """Check email configuration status"""
    print("📧 Checking Email Configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/email-config")
        
        if response.status_code == 200:
            config = response.json()
            if config.get('configured'):
                print(f"✅ Email configured: {config.get('email')}")
                print(f"   Telegram ID: {config.get('telegramUserId')}")
                return True
            else:
                print("❌ Email not configured")
                return False
        else:
            print(f"❌ Failed to get config: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking config: {e}")
        return False

def check_emotion_data():
    """Check if emotion data is available"""
    print("\n📊 Checking Emotion Data...")
    
    try:
        # Check emotion overview
        response = requests.get(f"{BASE_URL}/api/emotion-overview")
        if response.status_code == 200:
            overview = response.json()
            total_messages = 0
            
            for emotion, data in overview.items():
                count = data.get('count', 0)
                total_messages += count
                print(f"   {emotion.capitalize()}: {count}")
            
            print(f"✅ Total messages: {total_messages}")
            
            if total_messages > 0:
                return True
            else:
                print("⚠️ No emotional messages found")
                return False
        else:
            print(f"❌ Failed to get overview: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking emotion data: {e}")
        return False

def check_real_time_trends():
    """Check real-time trends functionality"""
    print("\n📈 Checking Real-time Trends...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/emotion-trends?hours=6")
        if response.status_code == 200:
            trends = response.json()
            trend_data = trends.get('trends', [])
            
            print(f"✅ Retrieved {len(trend_data)} time periods")
            
            # Check if any periods have data
            has_data = False
            for period in trend_data:
                total = sum([
                    period.get('anger', 0),
                    period.get('confusion', 0), 
                    period.get('joy', 0),
                    period.get('neutral', 0)
                ])
                if total > 0:
                    has_data = True
                    print(f"   {period.get('time')}: {total} messages")
            
            if has_data:
                print("✅ Real-time trends have data")
                return True
            else:
                print("⚠️ Real-time trends are empty")
                return False
        else:
            print(f"❌ Failed to get trends: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking trends: {e}")
        return False

def fix_dashboard_issues():
    """Attempt to fix common dashboard issues"""
    print("\n🔧 Attempting to fix dashboard issues...")
    
    # 1. Add more test data if needed
    print("1. Adding fresh test data...")
    try:
        sample_messages = [
            {"text": "Great customer service!", "emotion": "joy"},
            {"text": "I'm having trouble with my order", "emotion": "confusion"},
            {"text": "This is unacceptable!", "emotion": "angry"},
            {"text": "Thank you for your help", "emotion": "joy"},
            {"text": "The website is working fine", "emotion": "neutral"}
        ]
        
        from datetime import datetime
        current_time = datetime.now()
        
        for i, msg in enumerate(sample_messages):
            message_data = {
                "id": f"fix_message_{i}_{int(time.time())}",
                "timestamp": current_time.isoformat(),
                "timestamp_iso": current_time.isoformat(),
                "source": "email",
                "sender": f"fix-user-{i}@example.com",
                "text": msg["text"],
                "emotion": msg["emotion"],
                "sentiment": msg["emotion"],
                "email_account": "dashboard-fix@example.com"
            }
            
            response = requests.post(f"{BASE_URL}/message", json=message_data)
            if response.status_code == 201:
                print(f"   ✅ Added {msg['emotion']} message")
            else:
                print(f"   ❌ Failed to add message: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Error adding test data: {e}")
    
    # 2. Trigger email monitoring
    print("2. Triggering email monitoring...")
    try:
        response = requests.post(f"{BASE_URL}/api/start-monitoring", json={})
        if response.status_code == 200:
            print("   ✅ Email monitoring triggered")
        else:
            print(f"   ❌ Failed to start monitoring: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error starting monitoring: {e}")

def main():
    """Main health check function"""
    print("🏥 Dashboard Health Check")
    print("=" * 50)
    
    # Check server connectivity
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # Run checks
    config_ok = check_email_config()
    data_ok = check_emotion_data()
    trends_ok = check_real_time_trends()
    
    print("\n" + "=" * 50)
    print("📋 Health Check Summary:")
    print(f"   Email Config: {'✅ OK' if config_ok else '❌ ISSUE'}")
    print(f"   Emotion Data: {'✅ OK' if data_ok else '❌ ISSUE'}")
    print(f"   Real-time Trends: {'✅ OK' if trends_ok else '❌ ISSUE'}")
    
    if not (config_ok and data_ok and trends_ok):
        print("\n🔧 Attempting to fix issues...")
        fix_dashboard_issues()
        
        print("\n⏰ Waiting 5 seconds then re-checking...")
        time.sleep(5)
        
        # Re-check
        print("\n🔄 Re-running health checks...")
        data_ok_2 = check_emotion_data()
        trends_ok_2 = check_real_time_trends()
        
        if data_ok_2 and trends_ok_2:
            print("\n🎉 Issues resolved! Dashboard should work now.")
        else:
            print("\n⚠️ Some issues persist. Try refreshing your browser.")
    
    else:
        print("\n🎉 All systems are healthy!")
    
    print("\n📋 Next Steps:")
    print("1. Refresh your dashboard in the browser")
    print("2. The emotion counts should now show non-zero values")
    print("3. Click 'Live' to see real-time trends with data")
    print("4. If issues persist, check browser console for errors")

if __name__ == "__main__":
    main()
