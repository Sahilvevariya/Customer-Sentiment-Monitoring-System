#!/usr/bin/env python3
"""
Quick system status checker
"""
import requests
import subprocess
import sys
from database import DatabaseManager

def check_status():
    print("🔍 QUICK STATUS CHECK")
    print("=" * 30)
    
    # Check database
    try:
        db_manager = DatabaseManager()
        db = db_manager.db
        messages = list(db.messages.find({}))
        emotions = list(db.emotion_analytics.find({}))
        print(f"✅ Database: {len(messages)} messages, {len(emotions)} emotion records")
    except Exception as e:
        print(f"❌ Database: {e}")
    
    # Check Flask server
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        print("✅ Flask server: Running")
    except:
        try:
            response = requests.get('http://localhost:5000/', timeout=2)
            print("✅ Flask server: Running (no health endpoint)")
        except:
            print("❌ Flask server: Not responding")
    
    # Check if any Python processes are running (Flask)
    try:
        result = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        if 'python.exe' in result.stdout:
            print("✅ Python processes: Running")
        else:
            print("⚠️ Python processes: None found")
    except:
        print("⚠️ Cannot check Python processes")
    
    print("\n💡 TO START EVERYTHING:")
    print("1. Backend: python app.py")
    print("2. Frontend: npm run dev")
    print("3. Open: http://localhost:3000")

if __name__ == "__main__":
    check_status()
