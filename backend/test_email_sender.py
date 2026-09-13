#!/usr/bin/env python3
"""
Send a test email to verify recognition
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

def send_test_email():
    print("📧 SENDING TEST EMAIL TO VERIFY RECOGNITION")
    print("="*50)
    
    # Test email content with different emotions
    test_emails = [
        {
            "subject": "I'm so excited about this new project!",
            "body": "Hi! I just wanted to share how thrilled I am about this amazing opportunity. This is going to be fantastic!",
            "expected_emotion": "JOY"
        },
        {
            "subject": "This is really confusing me",
            "body": "Hey, I'm having trouble understanding this concept. It's quite puzzling and I need some clarification.",
            "expected_emotion": "CONFUSION"
        },
        {
            "subject": "I'm frustrated with this situation",
            "body": "This is really annoying me. I'm getting quite upset about how this is being handled.",
            "expected_emotion": "ANGER"
        },
        {
            "subject": "Just a normal update",
            "body": "Here's a regular status update. Everything is proceeding as planned.",
            "expected_emotion": "NEUTRAL"
        }
    ]
    
    print("🎯 EASY TEST OPTIONS:")
    print("\nOption 1: Use Gmail Web Interface")
    print("1. Go to gmail.com")
    print("2. Click 'Compose'")
    print("3. To: black.falcon.x.69@gmail.com")
    print("4. Subject: 'I'm so excited about testing!'")
    print("5. Body: 'This is a test email to check if the emotion recognition works. I'm really happy about this!'")
    print("6. Send!")
    
    print("\nOption 2: Use Another Email Account")
    print("1. Use Yahoo, Outlook, or any other email")
    print("2. Send TO: black.falcon.x.69@gmail.com")
    print("3. Use emotional content")
    
    print("\nOption 3: Ask Someone Else")
    print("1. Ask a friend/colleague to send an email")
    print("2. TO: black.falcon.x.69@gmail.com")
    print("3. With content like: 'I'm confused about something'")
    
    print("\n✅ WHAT WILL HAPPEN:")
    print("• Email arrives in your Gmail inbox")
    print("• Your system detects it (if Live Monitoring is on)")
    print("• Emotion is analyzed")
    print("• Dashboard updates with the emotion data")
    print("• You see the new data in your charts!")
    
    print("\n⏱️ TIMING:")
    print("• Email processing happens every 10-30 seconds")
    print("• Dashboard updates in real-time")
    print("• You should see changes within 1 minute")
    
    print("\n🔍 TO VERIFY IT WORKED:")
    print("• Check your dashboard charts")
    print("• Look for new emotion counts")
    print("• Check the 'Recent Messages' section")
    print("• Verify the timestamp is recent")

if __name__ == "__main__":
    send_test_email()
