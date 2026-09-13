#!/usr/bin/env python3
"""
Quick script to add sample emotional data for testing real-time trends
"""
import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://127.0.0.1:5000"

# Sample emotional messages
SAMPLE_MESSAGES = [
    {"text": "I'm extremely frustrated with this service!", "emotion": "angry"},
    {"text": "This is amazing! I love it!", "emotion": "joy"}, 
    {"text": "I'm confused about how this works", "emotion": "confusion"},
    {"text": "Thank you for the quick response", "emotion": "joy"},
    {"text": "This is terrible, I want a refund!", "emotion": "angry"},
    {"text": "The information provided is helpful", "emotion": "neutral"},
    {"text": "I'm not sure what to do next", "emotion": "confusion"},
    {"text": "Outstanding service, keep it up!", "emotion": "joy"},
    {"text": "I'm disappointed with the outcome", "emotion": "angry"},
    {"text": "The process is straightforward", "emotion": "neutral"},
]

def add_sample_messages():
    """Add sample messages with varied timestamps for testing real-time trends"""
    print("🧪 Adding sample emotional messages for testing...")
    
    current_time = datetime.now()
    
    for i, sample in enumerate(SAMPLE_MESSAGES):
        # Create messages at different times within the last 3 hours
        time_offset = random.randint(0, 180)  # 0 to 180 minutes ago
        message_time = current_time - timedelta(minutes=time_offset)
        
        message_data = {
            "id": f"test_message_{i}",
            "timestamp": message_time.strftime("%a, %d %b %Y %H:%M:%S %z"),
            "timestamp_iso": message_time.isoformat(),
            "source": "email",
            "sender": f"test-user-{i}@example.com", 
            "text": sample["text"],
            "emotion": sample["emotion"],
            "sentiment": sample["emotion"],
            "user_id": "test_user",
            "email_account": "black.falcon.x.69@gmail.com",
            "priority": "high" if sample["emotion"] == "angry" else "medium" if sample["emotion"] == "confusion" else "low"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/message", json=message_data)
            if response.status_code == 201:
                print(f"✅ Added {sample['emotion']} message: {sample['text'][:50]}...")
            else:
                print(f"❌ Failed to add message: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error adding message: {e}")
    
    print("🎉 Sample messages added! Check the dashboard now.")

def test_emotion_trends():
    """Test the emotion trends endpoint"""
    print("\n📊 Testing emotion trends endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/emotion-trends", params={"hours": 6})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Emotion trends retrieved successfully")
            print(f"Time range: {data.get('time_range_hours')} hours")
            
            trends = data.get('trends', [])
            total_emotions = {"anger": 0, "confusion": 0, "joy": 0, "neutral": 0}
            
            for trend in trends:
                for emotion in total_emotions:
                    total_emotions[emotion] += trend.get(emotion, 0)
            
            print(f"📈 Total emotions found: {total_emotions}")
            
            if sum(total_emotions.values()) > 0:
                print("🎉 Real-time trends should now show data!")
            else:
                print("⚠️ No emotional data found in trends")
        else:
            print(f"❌ Failed to get trends: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing trends: {e}")

def test_emotion_overview():
    """Test the emotion overview endpoint"""
    print("\n📊 Testing emotion overview endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/emotion-overview")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Emotion overview retrieved successfully")
            
            for emotion, info in data.items():
                count = info.get('count', 0)
                percentage = info.get('change_percent', 0)
                print(f"  {emotion.capitalize()}: {count} messages ({percentage}%)")
        else:
            print(f"❌ Failed to get overview: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing overview: {e}")

def main():
    """Main function to populate test data"""
    print("🚀 Real-time Emotion Trends Test Data Generator")
    print("=" * 60)
    
    # Add sample messages
    add_sample_messages()
    
    # Test the endpoints
    test_emotion_trends()
    test_emotion_overview()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("\n📋 What to do next:")
    print("1. Refresh your dashboard to see the emotion counts")
    print("2. Click the 'Live' button to see real-time trends")
    print("3. The chart should now show emotional data over time")
    print("4. Try adding more test data by running this script again")

if __name__ == "__main__":
    main()
