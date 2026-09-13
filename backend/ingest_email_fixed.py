import imaplib
import email
from email.header import decode_header
import requests
import time
from datetime import datetime
from dateutil import parser as date_parser
from gemini_emotion_classifier import classify_emotion_with_gemini
from database import get_database_manager

def clean_subject(subject):
    if not subject:
        return ""
    try:
        decoded, charset = decode_header(subject)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(charset or 'utf-8', errors='ignore')
        return str(decoded)
    except Exception:
        return str(subject)

def get_email_config(user_id=None):
    """Get email configuration from database for specific user or globally"""
    try:
        db_manager = get_database_manager()
        config = db_manager.get_email_config(user_id)
        if config:
            return {
                'email': config.get('email'),
                'password': config.get('app_password'),
                'telegram_user_id': config.get('telegram_user_id'),
                'user_id': config.get('user_id'),
                'imap_server': 'imap.gmail.com'  # Default for Gmail
            }
        else:
            user_msg = f" for user {user_id}" if user_id else ""
            print(f"⚠️ No email configuration found{user_msg}. Please configure email monitoring first.")
            return None
    except Exception as e:
        print(f"❌ Error fetching email config: {e}")
        return None

def test_email_connection(user_id=None):
    """Test email connection with stored configuration for specific user"""
    try:
        config = get_email_config(user_id)
        if not config:
            return {"success": False, "error": "No email configuration found"}
        
        EMAIL = config['email']
        PASSWORD = config['password']
        IMAP_SERVER = config['imap_server']
        
        user_msg = f" for user {user_id}" if user_id else ""
        print(f"🧪 Testing email connection{user_msg}: {EMAIL}")
        
        # Test IMAP connection
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        
        # Test search functionality
        status, messages = mail.search(None, 'ALL')
        if status != 'OK':
            return {"success": False, "error": "Failed to search inbox"}
        
        mail.logout()
        
        print(f"✅ Email connection successful{user_msg}: {EMAIL}")
        return {"success": True, "message": f"Connection successful for {EMAIL}"}
        
    except imaplib.IMAP4.error as e:
        error_msg = f"IMAP error: {str(e)}"
        print(f"❌ Email connection failed: {error_msg}")
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        print(f"❌ Email connection failed: {error_msg}")
        return {"success": False, "error": error_msg}

def fetch_and_forward_emails(specific_email=None, specific_password=None, user_id=None):
    """
    Fetch emails from configured or specified email account
    Args:
        specific_email: Optional specific email to fetch from
        specific_password: Optional specific password for the email
        user_id: Optional user ID to fetch emails for (overrides specific_email/password)
    """
    # Get email configuration from database or use provided credentials
    if user_id:
        # Priority 1: Use user_id to get stored configuration
        config = get_email_config(user_id)
        if not config:
            print(f"❌ Cannot fetch emails: No email configuration found for user {user_id}")
            return
        print(f"📧 Using stored configuration for user {user_id}: {config['email']}")
    elif specific_email and specific_password:
        # Priority 2: Use provided credentials
        config = {
            'email': specific_email,
            'password': specific_password,
            'imap_server': 'imap.gmail.com',
            'telegram_user_id': None,  # Will need to get from database or default
            'user_id': None  # Temporary user for this session
        }
        print(f"📧 Using provided credentials for: {specific_email}")
    else:
        # Priority 3: Use global configuration (backward compatibility)
        config = get_email_config()
        if not config:
            print("❌ Cannot fetch emails: No email configuration found")
            return
        print(f"📧 Using global stored configuration for: {config['email']}")
    
    EMAIL = config['email']
    PASSWORD = config['password']
    IMAP_SERVER = config['imap_server']
    TELEGRAM_USER_ID = config.get('telegram_user_id')
    USER_ID = config.get('user_id') or user_id
    
    print(f"📧 Starting email monitoring for: {EMAIL}")
    
    try:
        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        # Search unread emails (limit to recent ones to avoid overwhelming)
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK':
            print(f"❌ Failed to search emails for {EMAIL}")
            mail.logout()
            return
            
        email_ids = messages[0].split()
        
        # Limit processing to avoid overwhelming the system and API quotas
        max_emails = 10  # Process only the 10 most recent unread emails
        if len(email_ids) > max_emails:
            email_ids = email_ids[-max_emails:]  # Get the most recent ones
            print(f"📨 Found {len(messages[0].split())} unread emails, processing {max_emails} most recent for {EMAIL}")
        else:
            print(f"📨 Found {len(email_ids)} unread emails for {EMAIL}")

        processed_count = 0
        success_count = 0

        for num in email_ids:
            processed_count += 1
            print(f"📧 Processing email {processed_count}/{len(email_ids)}...")
            
            try:
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status != 'OK':
                    print(f"❌ Failed to fetch email {num}")
                    continue
                    
                msg = email.message_from_bytes(msg_data[0][1])

                subject = clean_subject(msg.get("Subject", ""))
                sender = msg.get("From", "")
                date = msg.get("Date", "")

                # Get message body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode(errors="ignore")
                                    break
                            except Exception:
                                continue
                else:
                    try:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors="ignore")
                    except Exception:
                        body = ""

                full_text = f"Subject: {subject}\n\n{body.strip()}"

                # Call Gemini API to classify emotion with fallback
                try:
                    emotion = classify_emotion_with_gemini(full_text)
                    print(f"📊 Gemini classified emotion: {emotion}")
                except Exception as e:
                    print(f"⚠️ Gemini API failed: {e}")
                    # Simple fallback emotion classification
                    text_lower = full_text.lower()
                    if any(word in text_lower for word in ['angry', 'furious', 'hate', 'terrible', 'awful', 'worst', 'disgusted', 'outrageous']):
                        emotion = 'angry'
                    elif any(word in text_lower for word in ['thank', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'fantastic', 'perfect']):
                        emotion = 'happy'
                    elif any(word in text_lower for word in ['confused', 'unclear', 'help', 'question', 'understand', 'explain']):
                        emotion = 'confused'
                    else:
                        emotion = 'neutral'
                    print(f"📊 Fallback classified emotion: {emotion}")

                # Create proper timestamp for real-time tracking
                try:
                    # Parse email date to proper timestamp
                    email_timestamp = date_parser.parse(date)
                except Exception:
                    # Fallback to current time if parsing fails
                    email_timestamp = datetime.now()

                # Prepare data with emotion and user information
                message_data = {
                    "id": f"email_{num.decode()}",
                    "timestamp": email_timestamp.isoformat(),  # Use ISO format for JSON compatibility
                    "source": "email",
                    "sender": sender,
                    "text": full_text,
                    "emotion": emotion,
                    "sentiment": emotion,  # Add sentiment field for compatibility
                    "user_id": USER_ID,  # Associate with user
                    "email_account": EMAIL,  # Track which email account this came from
                    "priority": "high" if emotion.lower() in ['angry', 'frustrated', 'upset'] else "medium" if emotion.lower() in ['confused', 'concerned'] else "low"
                }

                # Forward to Flask app
                try:
                    response = requests.post("http://127.0.0.1:5000/message", json=message_data, timeout=10)
                    if response.status_code in [200, 201]:
                        print(f"✅ [{emotion.upper()}] Successfully processed email from: {sender}")
                        success_count += 1
                    else:
                        print(f"❌ [{emotion.upper()}] Failed to process email from: {sender} | Status: {response.status_code}")
                        print(f"Response: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ [{emotion.upper()}] Error sending email to Flask app: {e}")
                    
            except Exception as e:
                print(f"❌ Error processing individual email {num}: {e}")
                continue

        mail.logout()
        print(f"\n📧 Email monitoring cycle completed for {EMAIL}")
        print(f"📊 Summary: {success_count}/{processed_count} emails processed successfully")

    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP error during email fetch for {EMAIL}: {e}")
    except Exception as e:
        print(f"❌ Error during email fetch and send for {EMAIL}: {e}")

def fetch_all_user_emails():
    """Fetch emails from all configured user email accounts"""
    try:
        db_manager = get_database_manager()
        all_configs = db_manager.get_all_email_configs()
        
        if not all_configs:
            print("⚠️ No email configurations found. Using fallback to global config.")
            # Fallback to global config for backward compatibility
            fetch_and_forward_emails()
            return
        
        print(f"📧 Found {len(all_configs)} email configuration(s)")
        
        for config in all_configs:
            user_id = config.get('user_id')
            email = config.get('email', 'Unknown')
            
            try:
                if user_id:
                    print(f"🔄 Processing emails for user {user_id}: {email}")
                    fetch_and_forward_emails(user_id=user_id)
                else:
                    print(f"🔄 Processing emails for global config: {email}")
                    fetch_and_forward_emails()
                    
                # Small delay between accounts to avoid overwhelming the server
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing emails for {email}: {e}")
                continue
                
        print("✅ Completed processing all email accounts")
        
    except Exception as e:
        print(f"❌ Error in fetch_all_user_emails: {e}")
        # Fallback to single account processing
        fetch_and_forward_emails()

def continuous_email_monitoring(user_id=None):
    """Run email monitoring continuously with intervals
    Args:
        user_id: If provided, monitor only this user's email. If None, monitor all users.
    """
    if user_id:
        print(f"🔄 Starting continuous email monitoring for user {user_id}...")
        while True:
            try:
                fetch_and_forward_emails(user_id=user_id)
                print("⏰ Waiting 30 seconds before next check...")
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"❌ Error in continuous monitoring for user {user_id}: {e}")
                print("⏰ Waiting 60 seconds before retry...")
                time.sleep(60)  # Wait longer if there's an error
    else:
        print("🔄 Starting continuous email monitoring for all users...")
        while True:
            try:
                fetch_all_user_emails()
                print("⏰ Waiting 30 seconds before next check...")
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"❌ Error in continuous monitoring: {e}")
                print("⏰ Waiting 60 seconds before retry...")
                time.sleep(60)  # Wait longer if there's an error

if __name__ == "__main__":
    # For testing - run continuous monitoring
    continuous_email_monitoring()
