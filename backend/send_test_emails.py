#!/usr/bin/env python3
"""
Send test emails with different emotions to black.falcon.x.69@gmail.com
This will help test the emotion classification and reset functionality
"""

import requests
import json
from datetime import datetime, timedelta
import time
import random

BASE_URL = "http://localhost:5000"
TEST_EMAIL = "black.falcon.x.69@gmail.com"

# Test messages for each emotion type
EMAIL_TEMPLATES = {
    "angry": [
        {
            "subject": "Extremely Disappointed with Service",
            "body": "I am absolutely furious with the terrible service I received! This is completely unacceptable and I demand immediate action. Your company has failed me completely and I want a full refund right now. This is the worst customer experience I have ever had!",
            "sender": "angry.customer1@example.com"
        },
        {
            "subject": "Outrageous Billing Error - Fix This NOW!",
            "body": "I just discovered that you charged me twice for the same service! This is outrageous and I'm sick of your incompetent billing department. I want this fixed immediately or I'm taking legal action. Your customer service is absolutely terrible!",
            "sender": "frustrated.user@example.com"
        },
        {
            "subject": "Defective Product - Completely Useless!",
            "body": "The product I ordered is complete garbage! It doesn't work at all and your support team is useless. I'm disgusted with this company and will never buy from you again. This is a waste of my money and time!",
            "sender": "angry.buyer@example.com"
        }
    ],
    "happy": [
        {
            "subject": "Amazing Service - Thank You!",
            "body": "I just wanted to express how thrilled I am with your excellent service! The team went above and beyond to help me, and I couldn't be happier with the results. You've gained a customer for life. Keep up the fantastic work!",
            "sender": "satisfied.customer@example.com"
        },
        {
            "subject": "Outstanding Product Quality!",
            "body": "I'm absolutely delighted with my recent purchase! The quality exceeded my expectations and the delivery was super fast. Your customer service team was wonderful to work with. I'll definitely recommend you to all my friends!",
            "sender": "happy.buyer@example.com"
        },
        {
            "subject": "Perfect Solution - Exactly What I Needed!",
            "body": "Your product solved exactly the problem I was facing! I'm so grateful for the excellent support and the quick resolution. The whole experience has been fantastic from start to finish. Thank you so much!",
            "sender": "grateful.user@example.com"
        }
    ],
    "confused": [
        {
            "subject": "Need Help Understanding My Order",
            "body": "Hi, I'm a bit confused about my recent order. I received an email confirmation but I'm not sure what happens next. Could you please explain the process? I'm also unclear about the delivery timeline. Any clarification would be helpful.",
            "sender": "confused.customer@example.com"
        },
        {
            "subject": "Questions About Your Service",
            "body": "I'm interested in your service but I have several questions. I'm not clear on the pricing structure and what's included in each plan. Could someone please explain the differences? I'm also unsure about the setup process.",
            "sender": "uncertain.user@example.com"
        },
        {
            "subject": "Can't Figure Out How This Works",
            "body": "I've been trying to use your platform but I'm having trouble understanding how it works. The interface is confusing and I can't find the features I need. Could you provide some guidance or tutorial? I'm lost here.",
            "sender": "puzzled.customer@example.com"
        }
    ],
    "neutral": [
        {
            "subject": "Order Status Inquiry",
            "body": "Hello, I placed an order last week (Order #12345) and would like to check on its status. Could you please provide an update on when it will be shipped? Thank you for your time.",
            "sender": "regular.customer@example.com"
        },
        {
            "subject": "Account Information Update",
            "body": "I need to update my account information, specifically my billing address. Please let me know the procedure for making these changes. I would also like to update my contact phone number.",
            "sender": "standard.user@example.com"
        },
        {
            "subject": "General Information Request",
            "body": "I would like more information about your company's return policy and warranty terms. Please send me the relevant documentation. Also, are there any upcoming promotions I should be aware of?",
            "sender": "info.seeker@example.com"
        }
    ]
}

def send_email_message(emotion_type, template, delay_seconds=2):
    """Send an email message to the API for processing"""
    
    # Create message payload with correct fields for the API
    message_data = {
        "id": f"test_{emotion_type}_{int(time.time()*1000)}",  # Unique ID
        "timestamp": datetime.now().isoformat(),
        "source": "email",  # Required field
        "sender": template["sender"],
        "text": f"Subject: {template['subject']}\n\n{template['body']}",  # Combined subject and body
        "recipient": TEST_EMAIL,  # Additional info
        "user_id": "default_user",  # For user-specific tracking
        "expected_emotion": emotion_type  # For verification
    }
    
    try:
        print(f"📧 Sending {emotion_type.upper()} email: '{template['subject'][:50]}...'")
        
        response = requests.post(f"{BASE_URL}/message", json=message_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            classified_emotion = result.get('sentiment', result.get('emotion', 'unknown'))
            print(f"   ✅ Sent successfully - Classified as: {classified_emotion}")
            
            # Check if classification matches expected
            if classified_emotion.lower() == emotion_type.lower():
                print(f"   🎯 Correct classification!")
            elif (emotion_type == 'angry' and classified_emotion.lower() == 'anger') or \
                 (emotion_type == 'happy' and classified_emotion.lower() == 'joy') or \
                 (emotion_type == 'confused' and classified_emotion.lower() == 'confusion'):
                print(f"   🎯 Correct classification! ({classified_emotion})")
            else:
                print(f"   ⚠️  Expected {emotion_type}, got {classified_emotion}")
            
            return True
        else:
            print(f"   ❌ Failed to send: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error sending email: {e}")
        return False
    
    # Wait between sends to avoid overwhelming the system
    time.sleep(delay_seconds)

def check_emotion_status():
    """Check current emotion counts"""
    try:
        response = requests.get(f"{BASE_URL}/api/emotion-overview")
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n📊 Current Emotion Status:")
            print("=" * 40)
            
            total_messages = 0
            for emotion, data in result.items():
                if isinstance(data, dict) and 'count' in data:
                    count = data['count']
                    percentage = data.get('percentage_text', 'N/A')
                    total_messages += count
                    
                    icon = {'anger': '🔴', 'joy': '🟢', 'confusion': '🟡', 'neutral': '⚪'}.get(emotion, '⚫')
                    print(f"{icon} {emotion.title()}: {count} messages ({percentage})")
            
            print(f"\n📈 Total Messages: {total_messages}")
            return result
        else:
            print("❌ Failed to get emotion status")
            return None
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return None

def reset_data_for_fresh_test():
    """Reset all data before starting the test"""
    try:
        print("🔄 Resetting all emotion data for fresh test...")
        response = requests.post(f"{BASE_URL}/api/reset-emotion-data", 
                               json={"user_id": "default_user"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Data reset: {result['message']}")
            return True
        else:
            print(f"❌ Failed to reset data: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error resetting data: {e}")
        return False

def main():
    print("🚀 EMAIL EMOTION TESTING SYSTEM")
    print(f"📧 Target Email: {TEST_EMAIL}")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Flask server not responding. Please start the server first.")
            return
    except:
        print("❌ Cannot connect to Flask server. Please start the server first.")
        return
    
    print("✅ Connected to Flask server")
    
    # Reset data for fresh start
    if not reset_data_for_fresh_test():
        print("⚠️ Could not reset data, continuing anyway...")
    
    # Check initial status (should be zero)
    print("\n📊 Initial Status (should be zero after reset):")
    check_emotion_status()
    
    print(f"\n🎯 Starting to send test emails to {TEST_EMAIL}")
    print("=" * 60)
    
    total_sent = 0
    successful_sends = 0
    
    # Send emails for each emotion type
    for emotion_type, templates in EMAIL_TEMPLATES.items():
        print(f"\n🎭 Sending {emotion_type.upper()} emails:")
        print("-" * 40)
        
        for i, template in enumerate(templates, 1):
            print(f"  [{i}/3] ", end="")
            if send_email_message(emotion_type, template, delay_seconds=3):
                successful_sends += 1
            total_sent += 1
    
    # Final status check
    print(f"\n🏁 EMAIL SENDING COMPLETE")
    print("=" * 60)
    print(f"📊 Summary: {successful_sends}/{total_sent} emails sent successfully")
    
    # Wait a moment for processing
    print("\n⏳ Waiting 5 seconds for emotion processing...")
    time.sleep(5)
    
    # Check final emotion status
    final_status = check_emotion_status()
    
    # Verification
    print(f"\n✅ VERIFICATION:")
    print("-" * 30)
    if final_status:
        expected_counts = {emotion: 3 for emotion in EMAIL_TEMPLATES.keys()}
        
        for emotion, expected_count in expected_counts.items():
            # Map emotion names (API uses different names)
            api_emotion_name = {
                'angry': 'anger',
                'happy': 'joy', 
                'confused': 'confusion',
                'neutral': 'neutral'
            }.get(emotion, emotion)
            
            if api_emotion_name in final_status:
                actual_count = final_status[api_emotion_name].get('count', 0)
                if actual_count >= 1:  # At least some were classified correctly
                    print(f"✅ {emotion.title()}: {actual_count} messages classified")
                else:
                    print(f"⚠️ {emotion.title()}: {actual_count} messages (expected some)")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Check your dashboard at http://localhost:3000")
    print(f"   2. Click 'Start Live' to see real-time updates")
    print(f"   3. Test reset functionality by changing email configuration")
    print(f"   4. Verify data starts from zero after reset")

if __name__ == "__main__":
    main()
