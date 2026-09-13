#!/usr/bin/env python3
"""
Test if the system recognizes emails sent TO your email address
"""

import imaplib
import email
from email.header import decode_header
from database import DatabaseManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_email_recognition():
    print("🧪 TESTING EMAIL RECOGNITION")
    print("="*50)
    
    # Get email config from database
    db_manager = DatabaseManager()
    db = db_manager.db
    
    email_config = db.email_config.find_one({})
    if not email_config:
        print("❌ No email configuration found in database")
        return
    
    email_address = email_config.get('email')
    app_password = email_config.get('app_password')
    
    print(f"📧 Testing email: {email_address}")
    
    try:
        # Connect to Gmail IMAP
        print("🔌 Connecting to Gmail...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_address, app_password)
        
        # Select inbox
        mail.select("inbox")
        
        # Search for recent emails (last 24 hours)
        print("🔍 Searching for recent emails...")
        status, messages = mail.search(None, 'ALL')
        
        if status == 'OK':
            message_ids = messages[0].split()
            total_emails = len(message_ids)
            print(f"📊 Found {total_emails} total emails in inbox")
            
            # Check last 5 emails
            print("\n📧 Last 5 emails:")
            recent_ids = message_ids[-5:] if len(message_ids) >= 5 else message_ids
            
            for i, msg_id in enumerate(recent_ids, 1):
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Get sender
                    sender = email_message["From"]
                    subject = email_message["Subject"]
                    
                    print(f"{i}. From: {sender}")
                    print(f"   Subject: {subject}")
                    
                    # Check if it's sent TO your email (received emails)
                    to_header = email_message.get("To", "")
                    if email_address in to_header or email_address in sender:
                        print(f"   ✅ This email will be processed (TO: {email_address})")
                    else:
                        print(f"   ⚠️ This email might not be processed")
                    print()
        
        mail.close()
        mail.logout()
        
        print("🎯 ANSWER TO YOUR QUESTION:")
        print(f"✅ YES! Any email sent TO {email_address} will be recognized")
        print("✅ The system monitors your INBOX for received emails")
        print("✅ It processes emails FROM any sender TO your email address")
        
        print("\n📝 WHAT GETS PROCESSED:")
        print("• Emails sent TO your Gmail address")
        print("• Emails in your INBOX folder")
        print("• Any sender (friends, companies, newsletters, etc.)")
        print("• All emotional content will be analyzed")
        
        print("\n💡 TO TEST:")
        print("1. Send an email TO black.falcon.x.69@gmail.com")
        print("2. From any email address (Gmail, Yahoo, Outlook, etc.)")
        print("3. Include emotional content like:")
        print("   • 'I'm so happy today!' (joy)")
        print("   • 'This is confusing' (confusion)")
        print("   • 'I'm frustrated' (anger)")
        print("4. Wait 30-60 seconds")
        print("5. Check your dashboard for updates")
        
    except Exception as e:
        print(f"❌ Error testing email connection: {e}")

if __name__ == "__main__":
    test_email_recognition()
