#!/usr/bin/env python3
"""
Test the fixed email processing with real emails
"""

from ingest_email import fetch_and_forward_emails
from database import DatabaseManager
import time

def test_fixed_email_processing():
    print("🧪 TESTING FIXED EMAIL PROCESSING")
    print("="*50)
    
    # Check current database state
    db_manager = DatabaseManager()
    db = db_manager.db
    
    before_messages = list(db.messages.find({}))
    before_emotions = list(db.emotion_analytics.find({}))
    
    print(f"📊 Before processing:")
    print(f"   Messages: {len(before_messages)}")
    print(f"   Emotion records: {len(before_emotions)}")
    
    # Process emails
    print(f"\n🔄 Processing recent emails...")
    fetch_and_forward_emails()
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Check after
    after_messages = list(db.messages.find({}))
    after_emotions = list(db.emotion_analytics.find({}))
    
    print(f"\n📊 After processing:")
    print(f"   Messages: {len(after_messages)}")
    print(f"   Emotion records: {len(after_emotions)}")
    
    new_messages = len(after_messages) - len(before_messages)
    print(f"\n✅ NEW MESSAGES PROCESSED: {new_messages}")
    
    if new_messages > 0:
        print("\n📧 Recent messages:")
        recent = list(db.messages.find({}).sort([('timestamp', -1)]).limit(3))
        for i, msg in enumerate(recent, 1):
            print(f"{i}. From: {msg.get('sender', 'Unknown')}")
            print(f"   Emotion: {msg.get('emotion', 'unknown')}")
            print(f"   Subject: {msg.get('text', 'No text')[:50]}...")
            print()
    
    print("🎯 EMAIL PROCESSING TEST COMPLETE!")
    return new_messages > 0

if __name__ == "__main__":
    test_fixed_email_processing()
