#!/usr/bin/env python3
"""
Debug script to check timestamp formats in database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from database import DatabaseManager
from datetime import datetime, timedelta

def debug_timestamps():
    print("🔍 Debugging timestamp formats...")
    
    db_manager = DatabaseManager()
    
    # Get latest few messages
    latest_messages = list(db_manager.messages.find().sort('_id', -1).limit(5))
    
    print("Latest 5 messages timestamp info:")
    for i, msg in enumerate(latest_messages, 1):
        print(f"\nMessage {i}:")
        print(f"  _id: {msg['_id']}")
        
        # Check all timestamp-related fields
        timestamp_fields = ['timestamp', 'created_at']
        for field in timestamp_fields:
            if field in msg:
                value = msg[field]
                print(f"  {field}: {value} (type: {type(value)})")
        
        # Check sentiment
        sentiment = msg.get('sentiment', msg.get('emotion', 'N/A'))
        text_preview = msg.get('text', 'N/A')[:40] + '...'
        print(f"  sentiment: {sentiment}")
        print(f"  text: {text_preview}")
    
    # Test current hour calculation
    print(f"\n⏰ Current time analysis:")
    now = datetime.now()
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)
    next_hour = current_hour_start + timedelta(hours=1)
    
    print(f"  Current time: {now}")
    print(f"  Current hour start: {current_hour_start}")
    print(f"  Next hour: {next_hour}")
    print(f"  Current hour start (ISO): {current_hour_start.isoformat()}")
    print(f"  Next hour (ISO): {next_hour.isoformat()}")
    
    # Test message count in current hour
    print(f"\n📊 Messages in current hour:")
    
    # Query using timestamp field
    current_hour_messages_timestamp = list(db_manager.messages.find({
        "timestamp": {
            "$gte": current_hour_start.isoformat(),
            "$lt": next_hour.isoformat()
        }
    }))
    print(f"  Using 'timestamp' field: {len(current_hour_messages_timestamp)} messages")
    
    # Query using created_at field
    current_hour_messages_created_at = list(db_manager.messages.find({
        "created_at": {
            "$gte": current_hour_start.isoformat(),
            "$lt": next_hour.isoformat()
        }
    }))
    print(f"  Using 'created_at' field: {len(current_hour_messages_created_at)} messages")
    
    # Query using either field
    current_hour_messages_either = list(db_manager.messages.find({
        "$or": [
            {
                "timestamp": {
                    "$gte": current_hour_start.isoformat(),
                    "$lt": next_hour.isoformat()
                }
            },
            {
                "created_at": {
                    "$gte": current_hour_start.isoformat(),
                    "$lt": next_hour.isoformat()
                }
            }
        ]
    }))
    print(f"  Using either field: {len(current_hour_messages_either)} messages")
    
    if current_hour_messages_either:
        print("  Messages found in current hour:")
        for msg in current_hour_messages_either:
            sentiment = msg.get('sentiment', msg.get('emotion', 'N/A'))
            timestamp = msg.get('timestamp', msg.get('created_at', 'N/A'))
            print(f"    {timestamp}: {sentiment}")

if __name__ == "__main__":
    debug_timestamps()
