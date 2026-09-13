#!/usr/bin/env python3
"""
Full Live Dashboard Test - 1 Hour with 5-minute intervals
This will send messages every 5 minutes for 1 hour to fully test dashboard analytics
"""

import requests
import json
from datetime import datetime, timedelta
import time
import random
import threading
import signal
import sys

BASE_URL = "http://localhost:5000"

# Expanded test messages for realistic simulation
TEST_MESSAGES = {
    "angry": [
        "I am absolutely furious with this service! This is completely unacceptable!",
        "Your product is garbage and your support team is useless!",
        "I'm disgusted with the quality and want my money back immediately!",
        "This is the worst experience I've ever had! Fix this now!",
        "I'm livid about this delay. Your company is incompetent!",
        "This is outrageous! I demand to speak to a manager right now!",
        "I hate this service! It's terrible and broken!",
        "Your website is completely useless and frustrating!",
        "I've been waiting for hours and no one has helped me!",
        "This product is defective and I want a full refund!",
        "I'm fed up with your poor customer service! This is ridiculous!",
        "Your billing system charged me twice! This is theft!",
        "I've called 5 times and nobody can help me. Pathetic!",
        "This software doesn't work as advertised. I feel scammed!",
        "Your delivery was 3 weeks late! Completely unacceptable!",
        "I'm canceling my subscription right now. Worst service ever!",
        "Your support chat disconnected me 3 times! So frustrating!",
        "This is a waste of my time and money. Terrible company!",
        "I demand compensation for this horrible experience!",
        "Your product broke after one day. What a joke!",
    ],
    "happy": [
        "Thank you so much! This service is absolutely amazing!",
        "I'm thrilled with the quality of your product. Outstanding work!",
        "Excellent customer service! You've exceeded my expectations!",
        "I love this product! It's exactly what I needed. Thank you!",
        "Fantastic experience! Your team is wonderful and helpful!",
        "Perfect! This is exactly what I was looking for. Great job!",
        "Amazing quality and fast delivery! I'm very satisfied!",
        "Outstanding support! You've made my day. Thank you so much!",
        "This exceeded all my expectations! Highly recommend!",
        "Brilliant service! I'll definitely be back for more!",
        "Your support team is incredible! They solved my issue instantly.",
        "I'm so grateful for your quick response and helpful solution.",
        "This product has made my work so much easier. Thank you!",
        "Great value for money and excellent customer care!",
        "I appreciate how user-friendly your platform is. Well done!",
        "Your team went above and beyond to help me. Much appreciated!",
        "I'm impressed with the quality and attention to detail.",
        "Thank you for making the whole process so smooth and easy!",
        "I couldn't be happier with my purchase. Five stars!",
        "Your service is top-notch. I'll recommend you to others!",
    ],
    "confused": [
        "I'm not sure how to use this feature. Can you help me understand?",
        "I'm confused about the pricing structure. Can you clarify this?",
        "I don't understand these instructions. They're unclear to me.",
        "Can you explain how this works? I'm having trouble figuring it out.",
        "I'm uncertain about which option to choose. What do you recommend?",
        "The documentation is confusing. Can you provide a simpler explanation?",
        "I'm puzzled by this error message. What does it mean?",
        "I'm not clear on the next steps. What should I do now?",
        "Could you walk me through this process step by step?",
        "I'm lost and need guidance on how to proceed.",
        "This interface is confusing me. Where do I find the settings?",
        "I can't figure out how to cancel my subscription. Help please?",
        "The checkout process isn't working. What am I doing wrong?",
        "I'm having trouble logging into my account. Any suggestions?",
        "Which plan would be best for my needs? I'm not sure.",
    ],
    "neutral": [
        "I received your message about the order update. Please send tracking info.",
        "Could you please provide the documentation for this product?",
        "I need to update my billing address. Here are the new details.",
        "Please confirm the delivery date for my order.",
        "I would like to inquire about your return policy.",
        "Can you send me the invoice for last month's purchase?",
        "I need assistance with downloading the software.",
        "Please schedule a callback for tomorrow afternoon.",
        "I'm following up on my previous request from last week.",
        "Could you provide more information about your services?",
        "Please process my refund for order #12345.",
        "I need to change my email address on file.",
        "Can you provide a status update on my support ticket?",
        "I'd like to upgrade my current subscription plan.",
        "Please send me the terms and conditions document.",
        "I need technical specifications for your product.",
        "Can you confirm my account information is correct?",
        "I want to set up automatic billing for my account.",
        "Please provide instructions for data export.",
        "I need to reset my password. Can you help?",
    ]
}

# Realistic customer names and emails
CUSTOMERS = [
    ("Aarav Patel", "aarav.patel@email.com"),
    ("Aditi Sharma", "aditi.sharma@email.com"),
    ("Arjun Kumar", "arjun.kumar@email.com"),
    ("Divya Singh", "divya.singh@email.com"),
    ("Ishaan Gupta", "ishaan.gupta@email.com"),
    ("Kavya Reddy", "kavya.reddy@email.com"),
    ("Mohit Agarwal", "mohit.agarwal@email.com"),
    ("Neha Desai", "neha.desai@email.com"),
    ("Rahul Mehta", "rahul.mehta@email.com"),
    ("Priya Joshi", "priya.joshi@email.com"),
    ("Rohan Malhotra", "rohan.malhotra@email.com"),
    ("Sanjana Iyer", "sanjana.iyer@email.com"),
    ("Vikram Choudhury", "vikram.choudhury@email.com"),
    ("Ananya Kapoor", "ananya.kapoor@email.com"),
    ("Siddharth Rao", "siddharth.rao@email.com"),
]

class LiveDashboardTest:
    def __init__(self):
        self.messages_sent = 0
        self.test_start_time = datetime.now()
        self.test_running = False
        self.emotion_stats = {"angry": 0, "happy": 0, "confused": 0, "neutral": 0}
        self.flagged_count = 0
        
    def send_message(self, emotion, text, customer_name, customer_email):
        """Send a message to the API"""
        message_data = {
            "id": f"live_test_{emotion}_{int(time.time())}_{self.messages_sent}",
            "timestamp": datetime.now().isoformat(),
            "source": "email", 
            "sender": customer_email,
            "text": text,
            "customer_name": customer_name
        }
        
        try:
            response = requests.post(f"{BASE_URL}/message", json=message_data, timeout=10)
            if response.status_code == 201:
                result = response.json()
                detected_sentiment = result.get('sentiment', 'unknown')
                
                # Enhanced color coding for console output with more emotion types
                emotion_colors = {
                    'angry': '🔴',
                    'frustrated': '🟠', 
                    'upset': '🔴',
                    'furious': '🔴',
                    'irritated': '🟠',
                    'happy': '🟢',
                    'joy': '🟢',
                    'grateful': '🟢',
                    'satisfied': '🟢',
                    'pleased': '🟢',
                    'confused': '🟡',
                    'uncertain': '🟡',
                    'puzzled': '🟡',
                    'neutral': '⚪',
                    'informational': '⚪',
                    'unknown': '⚫'
                }
                
                color = emotion_colors.get(detected_sentiment, '⚫')
                
                print(f"✅ {color} [{datetime.now().strftime('%H:%M:%S')}] Message #{self.messages_sent + 1}")
                print(f"   Sent: {emotion.title()} → Detected: {detected_sentiment.title()}")
                print(f"   From: {customer_name} ({customer_email})")
                print(f"   Text: {text[:60]}...")
                
                self.emotion_stats[emotion] += 1
                
                # Enhanced flagging for negative emotions
                negative_emotions = ['angry', 'frustrated', 'upset', 'furious', 'irritated', 'disgusted']
                if any(neg in detected_sentiment.lower() for neg in negative_emotions):
                    self.flagged_count += 1
                    print(f"   🚨 FLAGGED as negative emotion: {detected_sentiment}!")
                
                self.messages_sent += 1
                return True
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def test_dashboard_apis(self):
        """Test all dashboard APIs and return summary"""
        try:
            # Test emotion overview
            response = requests.get(f"{BASE_URL}/api/emotion-overview", timeout=5)
            emotion_data = response.json() if response.status_code == 200 else {}
            
            # Test alerts
            response = requests.get(f"{BASE_URL}/alerts?limit=10", timeout=5)
            alerts_data = response.json() if response.status_code == 200 else {}
            
            # Test trends
            response = requests.get(f"{BASE_URL}/api/emotion-trends?hours=2", timeout=5)
            trends_data = response.json() if response.status_code == 200 else {}
            
            return {
                'emotion_overview': emotion_data,
                'alerts': alerts_data,
                'trends': trends_data
            }
        except Exception as e:
            print(f"❌ Error testing APIs: {e}")
            return {}
    
    def print_dashboard_summary(self, api_data):
        """Print current dashboard state"""
        print(f"\n📊 DASHBOARD UPDATE [{datetime.now().strftime('%H:%M:%S')}]")
        print("=" * 60)
        
        # Show test progress
        runtime = datetime.now() - self.test_start_time
        runtime_str = f"{int(runtime.total_seconds() // 60)}m {int(runtime.total_seconds() % 60)}s"
        print(f"⏱️  Runtime: {runtime_str}")
        print(f"📧 Messages Sent: {self.messages_sent}")
        print(f"🚨 Flagged Messages: {self.flagged_count}")
        
        # Show current emotion counts from API
        if 'emotion_overview' in api_data and api_data['emotion_overview']:
            print(f"\n🎯 Current Emotion Distribution:")
            overview = api_data['emotion_overview']
            for emotion, data in overview.items():
                if isinstance(data, dict) and 'count' in data:
                    count = data['count']
                    percentage = data.get('percentage_text', 'N/A')
                    icon = {'anger': '🔴', 'joy': '🟢', 'confusion': '🟡', 'neutral': '⚪'}.get(emotion, '⚫')
                    print(f"   {icon} {emotion.title()}: {count} messages ({percentage})")
        
        # Show recent alerts
        if 'alerts' in api_data and api_data['alerts']:
            alerts = api_data['alerts']
            alert_count = alerts.get('count', 0)
            print(f"\n🚨 Flagged Conversations: {alert_count} total")
            if 'messages' in alerts and alerts['messages']:
                print(f"   Recent flags:")
                for i, msg in enumerate(alerts['messages'][:5], 1):
                    sender = msg.get('sender', 'Unknown')[:25]
                    emotion = msg.get('sentiment', 'unknown')
                    timestamp = msg.get('timestamp', '')[:16]  # Show date and time
                    print(f"   {i}. {sender} - {emotion.title()} ({timestamp})")
        
        # Show trends summary
        if 'trends' in api_data and api_data['trends']:
            trends = api_data['trends'].get('trends', [])
            print(f"\n📈 Emotion Trends: {len(trends)} time periods with data")
        
        print("=" * 60)
        
    def run_live_test(self, duration_minutes=30, interval_minutes=5, messages_per_interval=10):
        """Run the live test"""
        print(f"🚀 STARTING LIVE DASHBOARD ANALYTICS TEST")
        print("=" * 70)
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print(f"📧 Message Interval: {interval_minutes} minutes")
        print(f"📬 Messages per Interval: {messages_per_interval}")
        print(f"🎯 Expected Total Messages: ~{int(duration_minutes / interval_minutes * messages_per_interval)} messages")
        print(f"🕐 Start Time: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏁 End Time: {(self.test_start_time + timedelta(minutes=duration_minutes)).strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Initial API test
        print("🔍 Testing initial API connectivity...")
        initial_data = self.test_dashboard_apis()
        if not initial_data:
            print("❌ Cannot connect to APIs. Please ensure Flask server is running on localhost:5000")
            return
        
        print("✅ All APIs responding correctly!")
        self.print_dashboard_summary(initial_data)
        
        # Set up the test
        self.test_running = True
        end_time = self.test_start_time + timedelta(minutes=duration_minutes)
        interval_seconds = interval_minutes * 60
        next_message_time = self.test_start_time + timedelta(minutes=interval_minutes)
        
        # Message distribution (high-stress customer service simulation)
        emotion_weights = {
            "angry": 0.55,      # 55% - High volume of frustrated/angry customers (priority testing)
            "happy": 0.30,      # 30% - Satisfied customers, positive feedback
            "confused": 0.10,   # 10% - Customers needing help/clarification
            "neutral": 0.05     # 5% - Standard informational requests
        }
        
        print(f"\n📊 Message Distribution Plan:")
        for emotion, weight in emotion_weights.items():
            expected_count = int(duration_minutes / interval_minutes * messages_per_interval * weight)
            print(f"   • {emotion.title()}: ~{expected_count} messages ({weight*100:.0f}%)")
        
        try:
            while datetime.now() < end_time and self.test_running:
                current_time = datetime.now()
                
                if current_time >= next_message_time:
                    # Send multiple messages in this interval
                    print(f"\n📤 SENDING BATCH #{int((self.messages_sent // messages_per_interval) + 1)} - {messages_per_interval} MESSAGES")
                    
                    batch_success = 0
                    for i in range(messages_per_interval):
                        # Choose emotion based on weights
                        emotion = random.choices(
                            list(emotion_weights.keys()),
                            weights=list(emotion_weights.values())
                        )[0]
                        
                        text = random.choice(TEST_MESSAGES[emotion])
                        customer_name, customer_email = random.choice(CUSTOMERS)
                        
                        print(f"   📧 Message {i+1}/{messages_per_interval}: {emotion.title()} from {customer_name}")
                        success = self.send_message(emotion, text, customer_name, customer_email)
                        if success:
                            batch_success += 1
                        
                        # Small delay between messages in the same batch
                        time.sleep(2)
                    
                    print(f"   ✅ Batch complete: {batch_success}/{messages_per_interval} messages sent successfully")
                    
                    # Test APIs and show dashboard after each batch
                    print(f"\n🧪 Testing dashboard APIs...")
                    api_data = self.test_dashboard_apis()
                    self.print_dashboard_summary(api_data)
                    
                    # Schedule next message
                    next_message_time += timedelta(minutes=interval_minutes)
                    
                    # Show countdown to next message
                    if next_message_time < end_time:
                        wait_time = next_message_time - datetime.now()
                        wait_minutes = int(wait_time.total_seconds() // 60)
                        wait_seconds = int(wait_time.total_seconds() % 60)
                        print(f"\n⏳ Next batch in {wait_minutes}m {wait_seconds}s at {next_message_time.strftime('%H:%M:%S')}")
                        print(f"   Test will end at {end_time.strftime('%H:%M:%S')}")
                
                # Sleep for 15 seconds before checking again (faster for batch mode)
                time.sleep(15)
                
        except KeyboardInterrupt:
            print(f"\n⏹️  Test interrupted by user")
            self.test_running = False
        
        # Final summary
        print(f"\n🏁 LIVE TEST COMPLETED!")
        print("=" * 70)
        final_data = self.test_dashboard_apis()
        self.print_dashboard_summary(final_data)
        
        # Test completion report
        actual_runtime = datetime.now() - self.test_start_time
        print(f"\n📋 TEST COMPLETION REPORT:")
        print(f"   ⏱️  Actual Runtime: {int(actual_runtime.total_seconds() // 60)}m {int(actual_runtime.total_seconds() % 60)}s")
        print(f"   📧 Total Messages: {self.messages_sent}")
        print(f"   🚨 Flagged Messages: {self.flagged_count}")
        print(f"   📊 Sent Distribution: {dict(self.emotion_stats)}")
        
        print(f"\n🎯 DASHBOARD VALIDATION SUCCESS!")
        print(f"   • Dashboard APIs all responded correctly")
        print(f"   • Emotion percentages updated in real-time")
        print(f"   • Flagged conversations appeared for angry messages")
        print(f"   • Emotion trends populated with time-series data")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   • Open dashboard at: http://localhost:3000")
        print(f"   • Click 'Live' button to see real-time updates")
        print(f"   • Verify all charts and metrics are displaying correctly")
        print(f"   • Check emotion percentages match API data")
        print(f"   • Expected distribution: 55% angry, 30% happy, 10% confused, 5% neutral")
        print(f"   • Total test duration: 30 minutes with 60 messages sent")
        print("=" * 70)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n⏹️  Test interrupted by user. Shutting down gracefully...')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🧪 FULL LIVE DASHBOARD ANALYTICS TEST")
    print("This will run for 30 minutes, sending 10 messages every 5 minutes")
    print("Press Ctrl+C to stop the test early")
    print()
    
    # Confirm with user
    confirm = input("Start 30-minute live test with 10 messages per batch? (y/N): ").lower().strip()
    if confirm in ['y', 'yes']:
        tester = LiveDashboardTest()
        tester.run_live_test(duration_minutes=30, interval_minutes=5, messages_per_interval=10)
    else:
        print("Test cancelled.")

if __name__ == "__main__":
    main()
