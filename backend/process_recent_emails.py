#!/usr/bin/env python3
"""
Quick fix for email processing - process recent emails with fallback emotion classification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingest_email import get_email_config
import imaplib
import email
from email.header import decode_header
import requests
from datetime import datetime
from dateutil import parser as date_parser

def clean_subject(subject):
    if not subject:
        return ""
    decoded, charset = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or 'utf-8', errors='ignore')
    return decoded

def fallback_emotion_classifier(text):
    """Simple fallback emotion classification when Gemini API fails"""
    text_lower = text.lower()
    
    # Angry keywords
    angry_words = ['angry', 'furious', 'hate', 'terrible', 'awful', 'worst', 'disgusted', 'outrageous', 
                   'frustrated', 'annoyed', 'mad', 'upset', 'disappointed', 'unacceptable']
    
    # Happy keywords  
    happy_words = ['thank', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'fantastic', 'perfect',
                   'pleased', 'satisfied', 'delighted', 'awesome', 'brilliant', 'outstanding']
    
    # Confused keywords
    confused_words = ['confused', 'unclear', 'help', 'question', 'understand', 'explain', 'clarify',
                     'what', 'how', 'why', 'when', 'where', 'problem', 'issue', 'trouble']
    
    angry_score = sum(1 for word in angry_words if word in text_lower)
    happy_score = sum(1 for word in happy_words if word in text_lower)
    confused_score = sum(1 for word in confused_words if word in text_lower)
    
    if angry_score > happy_score and angry_score > confused_score:
        return 'angry'
    elif happy_score > confused_score:
        return 'happy'
    elif confused_score > 0:
        return 'confused'
    else:
        return 'neutral'

def process_recent_emails():
    """Process the 5 most recent unread emails"""
    print("📧 PROCESSING RECENT EMAILS")
    print("=" * 50)
    
    config = get_email_config()
    if not config:
        print("❌ No email configuration found!")
        return
    
    EMAIL = config['email']
    PASSWORD = config['password']
    IMAP_SERVER = config['imap_server']
    USER_ID = config.get('user_id') or 'default_user'
    
    print(f"📧 Connecting to: {EMAIL}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        # Search unread emails
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        # Process only the 5 most recent emails
        max_emails = 5
        if len(email_ids) > max_emails:
            email_ids = email_ids[-max_emails:]
            print(f"📨 Found {len(messages[0].split())} unread emails, processing {max_emails} most recent")
        else:
            print(f"📨 Found {len(email_ids)} unread emails")

        processed_count = 0
        success_count = 0

        for num in email_ids:
            processed_count += 1
            print(f"\n📧 Processing email {processed_count}/{len(email_ids)}...")
            
            try:
                status, msg_data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                subject = clean_subject(msg.get("Subject", ""))
                sender = msg.get("From", "")
                date = msg.get("Date", "")

                # Get message body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                full_text = f"Subject: {subject}\n\n{body.strip()}"
                
                # Use fallback emotion classification (skip Gemini to avoid quota issues)
                emotion = fallback_emotion_classifier(full_text)
                print(f"📊 Classified emotion: {emotion}")

                # Create timestamp
                try:
                    email_timestamp = date_parser.parse(date)
                except Exception:
                    email_timestamp = datetime.now()

                # Prepare message data
                message_data = {
                    "id": f"email_{num.decode()}_{int(datetime.now().timestamp())}",
                    "timestamp": email_timestamp.isoformat(),
                    "source": "email", 
                    "sender": sender,
                    "text": full_text[:1000],  # Limit text size
                    "sentiment": emotion,
                    "user_id": USER_ID,
                    "email_account": EMAIL
                }

                # Send to Flask app
                response = requests.post("http://127.0.0.1:5000/message", json=message_data, timeout=10)
                if response.status_code in [200, 201]:
                    print(f"✅ [{emotion.upper()}] Successfully processed!")
                    success_count += 1
                else:
                    print(f"❌ [{emotion.upper()}] Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error processing email: {e}")

        mail.logout()
        print(f"\n📊 Summary: {success_count}/{processed_count} emails processed successfully")
        
        if success_count > 0:
            print("✅ Your dashboard should now show updated emotion data!")
            print("🔄 Refresh your dashboard or click the 'Start Live' button to see updates")
        else:
            print("⚠️ No emails were successfully processed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    process_recent_emails()
