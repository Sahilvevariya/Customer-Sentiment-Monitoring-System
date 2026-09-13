#!/usr/bin/env python3
"""
Fixed email processing - directly process emails and update dashboard
"""

import imaplib
import email
from email.header import decode_header
import requests
from datetime import datetime
from dateutil import parser as date_parser
from database import get_database_manager

def clean_subject(subject):
    if not subject:
        return ""
    decoded, charset = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or 'utf-8', errors='ignore')
    return decoded

def get_email_config(user_id=None):
    """Get email configuration from database"""
    try:
        db_manager = get_database_manager()
        config = db_manager.get_email_config(user_id)
        if config:
            return {
                'email': config.get('email'),
                'password': config.get('app_password'),
                'telegram_user_id': config.get('telegram_user_id'),
                'user_id': config.get('user_id'),
                'imap_server': 'imap.gmail.com'
            }
        return None
    except Exception as e:
        print(f"❌ Error fetching email config: {e}")
        return None

def fallback_emotion_classifier(text):
    """Simple fallback emotion classification"""
    text_lower = text.lower()
    
    # Count emotional keywords
    angry_words = ['angry', 'furious', 'hate', 'terrible', 'awful', 'worst', 'disgusted', 'outrageous', 
                   'frustrated', 'annoyed', 'mad', 'upset', 'disappointed', 'unacceptable']
    happy_words = ['thank', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'fantastic', 'perfect',
                   'pleased', 'satisfied', 'delighted', 'awesome', 'brilliant', 'outstanding']
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

def process_emails_now():
    """Process recent emails and update dashboard"""
    print("🚀 PROCESSING REAL EMAILS FOR DASHBOARD UPDATE")
    print("=" * 60)
    
    config = get_email_config()
    if not config:
        print("❌ No email configuration found!")
        return
    
    EMAIL = config['email']
    PASSWORD = config['password']
    IMAP_SERVER = config['imap_server']
    USER_ID = config.get('user_id') or 'default_user'
    
    print(f"📧 Processing emails from: {EMAIL}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        # Get recent unread emails (limit to 5)
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        max_emails = 5
        if len(email_ids) > max_emails:
            email_ids = email_ids[-max_emails:]
            print(f"📨 Processing {max_emails} most recent of {len(messages[0].split())} unread emails")
        else:
            print(f"📨 Processing all {len(email_ids)} unread emails")

        success_count = 0

        for i, num in enumerate(email_ids, 1):
            print(f"\n📧 [{i}/{len(email_ids)}] Processing email...")
            
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
                        elif part.get_content_type() == "text/html" and not body:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                full_text = f"Subject: {subject}\n\n{body[:500]}"  # Limit body size
                
                # Classify emotion
                emotion = fallback_emotion_classifier(full_text)
                print(f"   📊 Sender: {sender[:50]}...")
                print(f"   📝 Subject: {subject[:50]}...")
                print(f"   😊 Emotion: {emotion}")

                # Create timestamp
                try:
                    email_timestamp = date_parser.parse(date)
                except Exception:
                    email_timestamp = datetime.now()

                # Prepare message for API
                message_data = {
                    "id": f"real_email_{int(datetime.now().timestamp() * 1000)}_{i}",
                    "timestamp": email_timestamp.isoformat(),
                    "source": "email",
                    "sender": sender,
                    "text": full_text,
                    "sentiment": emotion
                }

                # Send to Flask API
                response = requests.post("http://127.0.0.1:5000/message", json=message_data, timeout=10)
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ Successfully processed!")
                    success_count += 1
                else:
                    print(f"   ❌ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error processing email: {e}")

        mail.logout()
        
        print(f"\n🏁 PROCESSING COMPLETE")
        print("=" * 60)
        print(f"📊 Successfully processed: {success_count}/{len(email_ids)} emails")
        
        if success_count > 0:
            print("✅ Your dashboard should now show updated data!")
            print("🔄 Go to your dashboard and refresh, or click 'Start Live' to see the updates")
            
            # Check updated emotion data
            try:
                response = requests.get("http://localhost:5000/api/emotion-overview")
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n📈 Updated emotion counts:")
                    for emotion, info in data.items():
                        if isinstance(info, dict) and 'count' in info:
                            count = info['count']
                            print(f"   {emotion}: {count} messages")
            except:
                pass
        else:
            print("⚠️ No emails were processed successfully")
            
    except imaplib.IMAP4.error as e:
        print(f"❌ Gmail connection error: {e}")
        print("💡 Check your Gmail App Password and IMAP settings")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    process_emails_now()
