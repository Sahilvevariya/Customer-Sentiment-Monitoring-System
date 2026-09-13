#!/usr/bin/env python3
from database import DatabaseManager

# Initialize database
db_manager = DatabaseManager()
db = db_manager.db

# Check current status
messages = list(db.messages.find({}))
emotions = list(db.emotion_analytics.find({}))

print("📊 CURRENT DASHBOARD STATUS")
print("="*50)
print(f"Total messages: {len(messages)}")
print(f"Emotion records: {len(emotions)}")

print("\n🎭 Current emotion breakdown:")
for emotion in emotions:
    if emotion.get('count', 0) > 0:
        print(f"  {emotion['emotion']}: {emotion['count']} messages")

print(f"\n📧 Recent messages (last 3):")
recent = list(db.messages.find({}).sort([('timestamp', -1)]).limit(3))
for i, msg in enumerate(recent, 1):
    print(f"{i}. From: {msg.get('sender', 'Unknown')}")
    print(f"   Subject: {msg.get('subject', 'No subject')[:60]}...")
    print(f"   Emotion: {msg.get('emotion', 'unknown')}")
    print()
