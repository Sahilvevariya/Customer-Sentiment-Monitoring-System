from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from database import get_database_manager
from gemini_emotion_classifier import classify_emotion_with_gemini
from dotenv import load_dotenv
from chat_ticket_routes import chat_ticket_bp
from historical_sentiment_routes import historical_sentiment_bp



# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
app.register_blueprint(chat_ticket_bp)
app.register_blueprint(historical_sentiment_bp)

# Initialize database manager
try:
    # Check if required environment variables exist
    if not os.getenv('MONGODB_URI'):
        raise ValueError("MONGODB_URI environment variable is required")
    if not os.getenv('GEMINI_API_KEY'):
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    db_manager = get_database_manager()
    print("✅ Database connected successfully!")
except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    db_manager = None

@app.route('/')
def home():
    return "Customer Sentiment Watchdog is running!"

@app.route('/api/email-config', methods=['GET', 'POST'])
def email_config():
    """Email configuration endpoint - supports both global and user-specific configs"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    if request.method == 'GET':
        # Get user_id from query params only for GET requests
        user_id = request.args.get('user_id')
        
        try:
            # Get the email configuration for user or globally
            config = db_manager.get_email_config(user_id)
            if config:
                # Don't return the actual password for security
                response_data = {
                    "email": config.get("email"),
                    "telegramUserId": config.get("telegram_user_id"),
                    "configured": True,
                    "user_id": config.get("user_id")
                }
                return jsonify(response_data)
            else:
                return jsonify({"configured": False}), 404
        except Exception as e:
            return jsonify({"error": f"Failed to retrieve email config: {str(e)}"}), 500
    
    elif request.method == 'POST':
        # Get user_id from request body for POST requests
        try:
            data = request.get_json()
            user_id = data.get('user_id') if data else None
            
            # Validate required fields
            required_fields = ['email', 'appPassword', 'telegramUserId']
            if not data or not all(field in data for field in required_fields):
                return jsonify({"error": "Missing required fields: email, appPassword, telegramUserId"}), 400
            
            # Check if this is a new configuration (different email/password)
            existing_config = db_manager.get_email_config(user_id)
            is_new_config = not existing_config or \
                existing_config.get('email') != data['email'] or \
                existing_config.get('app_password') != data['appPassword']
            
            # Reset all data if this is a new configuration
            if is_new_config:
                print(f"🔄 New email configuration detected for user {user_id}, resetting all data...")
                try:
                    if user_id:
                        # Reset data for specific user
                        messages_result = db_manager.messages.delete_many({"user_id": user_id})
                        db_manager.analytics.delete_many({"user_id": user_id})
                        db_manager.history.delete_many({"user_id": user_id})
                        print(f"✅ Reset {messages_result.deleted_count} messages for user {user_id}")
                    else:
                        # Reset all data
                        messages_result = db_manager.messages.delete_many({})
                        db_manager.analytics.delete_many({})
                        db_manager.history.delete_many({})
                        print(f"✅ Reset {messages_result.deleted_count} total messages")
                except Exception as reset_error:
                    print(f"⚠️ Warning: Failed to reset data during config change: {reset_error}")
            
            # Save email configuration
            config_data = {
                "email": data['email'],
                "app_password": data['appPassword'],  # In production, encrypt this
                "telegram_user_id": data['telegramUserId'],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            config_id = db_manager.save_email_config(config_data, user_id)
            
            user_msg = f" for user {user_id}" if user_id else ""
            return jsonify({
                "message": f"Email configuration saved successfully{user_msg}",
                "config_id": config_id,
                "configured": True,
                "user_id": user_id,
                "data_reset": is_new_config  # Inform frontend that data was reset
            }), 201
            
        except Exception as e:
            return jsonify({"error": f"Failed to save email config: {str(e)}"}), 500

@app.route('/api/start-monitoring', methods=['POST'])
def start_monitoring():
    """Start email monitoring service for user or all users"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if user_id:
            # Check if specific user email configuration exists
            config = db_manager.get_email_config(user_id)
            if not config:
                return jsonify({"error": f"No email configuration found for user {user_id}. Please configure email monitoring first."}), 400
        else:
            # Check if at least one email configuration exists
            all_configs = db_manager.get_all_email_configs()
            if not all_configs:
                return jsonify({"error": "No email configurations found. Please configure email monitoring first."}), 400
        
        # Import email monitoring functions
        from ingest_email import fetch_and_forward_emails, fetch_all_user_emails
        
        # Run email monitoring in a separate thread to avoid blocking the request
        import threading
        
        def run_email_monitoring():
            try:
                if user_id:
                    print(f"🔄 Starting email monitoring for user {user_id}...")
                    fetch_and_forward_emails(user_id=user_id)
                else:
                    print("🔄 Starting email monitoring for all users...")
                    fetch_all_user_emails()
            except Exception as e:
                print(f"❌ Error in email monitoring: {e}")
        
        # Start monitoring in background thread
        monitoring_thread = threading.Thread(target=run_email_monitoring)
        monitoring_thread.daemon = True  # Dies when main thread dies
        monitoring_thread.start()
        
        if user_id:
            config = db_manager.get_email_config(user_id)
            return jsonify({
                "message": f"Email monitoring started for user {user_id}",
                "status": "monitoring",
                "email": config['email'],
                "user_id": user_id
            }), 200
        else:
            return jsonify({
                "message": "Email monitoring started for all configured users",
                "status": "monitoring"
            }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to start monitoring: {str(e)}"}), 500

@app.route('/api/test-email-config', methods=['GET'])
def test_email_config():
    """Test the email configuration by attempting to connect"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        user_id = request.args.get('user_id')
        
        # Check if email configuration exists
        config = db_manager.get_email_config(user_id)
        if not config:
            user_msg = f" for user {user_id}" if user_id else ""
            return jsonify({"error": f"No email configuration found{user_msg}"}), 400
        
        # Test email connection
        from ingest_email import test_email_connection
        
        result = test_email_connection(user_id)
        if result['success']:
            return jsonify({
                "message": "Email connection successful",
                "email": config['email'],
                "status": "connected",
                "user_id": user_id
            }), 200
        else:
            return jsonify({
                "error": f"Email connection failed: {result['error']}",
                "email": config['email'],
                "status": "failed",
                "user_id": user_id
            }), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to test email connection: {str(e)}"}), 500

@app.route('/api/fetch-emails-now', methods=['POST'])
def fetch_emails_now():
    """Fetch emails immediately with provided credentials or user ID"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        email = data.get('email')
        password = data.get('password')
        
        # Import email monitoring functions
        from ingest_email import fetch_and_forward_emails
        
        if user_id:
            # Fetch using stored configuration for user
            print(f"🔄 Fetching emails for user {user_id}...")
            fetch_and_forward_emails(user_id=user_id)
            config = db_manager.get_email_config(user_id)
            return jsonify({
                "message": f"Email fetch completed for user {user_id}",
                "email": config.get('email') if config else 'Unknown',
                "user_id": user_id
            }), 200
            
        elif email and password:
            # Fetch using provided credentials
            print(f"🔄 Fetching emails for provided credentials: {email}")
            fetch_and_forward_emails(specific_email=email, specific_password=password)
            return jsonify({
                "message": f"Email fetch completed for {email}",
                "email": email
            }), 200
            
        else:
            return jsonify({"error": "Either 'user_id' or both 'email' and 'password' are required"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to fetch emails: {str(e)}"}), 500

@app.route('/api/list-email-configs', methods=['GET'])
def list_email_configs():
    """List all configured email accounts"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        configs = db_manager.get_all_email_configs()
        
        # Remove sensitive information
        safe_configs = []
        for config in configs:
            safe_config = {
                "id": config.get("_id"),
                "email": config.get("email"),
                "user_id": config.get("user_id"),
                "telegram_user_id": config.get("telegram_user_id"),
                "created_at": config.get("created_at"),
                "updated_at": config.get("updated_at"),
                "active": config.get("active", True)
            }
            safe_configs.append(safe_config)
        
        return jsonify({
            "configs": safe_configs,
            "count": len(safe_configs)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to list email configs: {str(e)}"}), 500

@app.route('/api/reset-emotion-data', methods=['POST'])
def reset_emotion_data():
    """Reset all emotion data in the database - with enhanced user-specific support"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')  # Optional: reset data for specific user only
        
        print(f"🔄 Starting data reset for {'user ' + user_id if user_id else 'all users'}")
        
        if user_id:
            # Reset data for specific user
            messages_result = db_manager.messages.delete_many({"user_id": user_id})
            analytics_result = db_manager.analytics.delete_many({"user_id": user_id})
            history_result = db_manager.history.delete_many({"user_id": user_id})
            
            deleted_count = messages_result.deleted_count
            message = f"Emotion data reset for user {user_id}"
            
            print(f"✅ Reset complete for user {user_id}: {deleted_count} messages, {analytics_result.deleted_count} analytics, {history_result.deleted_count} history entries")
        else:
            # Reset all emotion data
            messages_result = db_manager.messages.delete_many({})
            analytics_result = db_manager.analytics.delete_many({})
            history_result = db_manager.history.delete_many({})
            
            deleted_count = messages_result.deleted_count
            message = f"All emotion data reset - starting fresh from zero"
            
            print(f"✅ Complete reset: {deleted_count} messages, {analytics_result.deleted_count} analytics, {history_result.deleted_count} history entries")
        
        return jsonify({
            "message": message,
            "deleted_messages": deleted_count,
            "status": "success",
            "reset_timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error resetting emotion data: {e}")
        return jsonify({"error": f"Failed to reset emotion data: {str(e)}"}), 500

@app.route('/api/start-live-monitoring', methods=['POST'])
def start_live_monitoring():
    """Start live email monitoring and fetching - ensures fresh start"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        email = data.get('email')
        password = data.get('password')
        reset_data = data.get('reset_data', True)  # Default to resetting data
        
        # Reset data before starting live monitoring if requested
        if reset_data:
            print(f"🔄 Resetting data before starting live monitoring...")
            try:
                if user_id:
                    # Reset data for specific user
                    messages_result = db_manager.messages.delete_many({"user_id": user_id})
                    db_manager.analytics.delete_many({"user_id": user_id})
                    db_manager.history.delete_many({"user_id": user_id})
                    print(f"✅ Reset {messages_result.deleted_count} messages for user {user_id}")
                else:
                    # Reset all data
                    messages_result = db_manager.messages.delete_many({})
                    db_manager.analytics.delete_many({})
                    db_manager.history.delete_many({})
                    print(f"✅ Reset {messages_result.deleted_count} total messages - starting from zero")
            except Exception as reset_error:
                print(f"⚠️ Warning: Failed to reset data before live monitoring: {reset_error}")
        
        # Import email monitoring functions
        from ingest_email import fetch_and_forward_emails, continuous_email_monitoring
        
        # Run email monitoring in background
        import threading
        
        def run_monitoring():
            try:
                if user_id:
                    print(f"🔴 Starting LIVE monitoring for user {user_id}...")
                    continuous_email_monitoring(user_id)
                elif email and password:
                    print(f"🔴 Starting LIVE monitoring for {email}...")
                    # Create a monitoring loop for specific credentials
                    import time
                    while True:
                        fetch_and_forward_emails(specific_email=email, specific_password=password)
                        time.sleep(30)  # Check every 30 seconds
                else:
                    print("🔴 Starting LIVE monitoring for all configured users...")
                    continuous_email_monitoring()
            except Exception as e:
                print(f"❌ Error in live monitoring: {e}")
        
        # Start monitoring in background thread
        monitoring_thread = threading.Thread(target=run_monitoring)
        monitoring_thread.daemon = True  # Dies when main thread dies
        monitoring_thread.start()
        
        response_data = {
            "message": "Live email monitoring started - data reset to zero",
            "status": "live_monitoring_active",
            "data_reset": reset_data,
            "start_timestamp": datetime.now().isoformat()
        }
        
        if user_id:
            response_data["user_id"] = user_id
        elif email:
            response_data["email"] = email
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to start live monitoring: {str(e)}"}), 500

@app.route('/message', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        return jsonify({
            "message": "Use POST to submit messages. This route accepts support messages from email/chat/tickets."
        }), 200

    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500

    data = request.get_json()

    # Validate input
    required_fields = ['id', 'timestamp', 'source', 'sender', 'text']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields in message"}), 400

    try:
        # Perform sentiment analysis if not already present
        if 'sentiment' not in data and 'emotion' not in data:
            print(f"🧠 Analyzing sentiment for message from {data.get('sender', 'unknown')}...")
            sentiment = classify_emotion_with_gemini(data['text'])
            data['sentiment'] = sentiment
            print(f"📊 Detected sentiment: {sentiment}")
        
        # Insert message into database
        message_id = db_manager.insert_message(data)
        total_messages = db_manager.get_message_count()
        
        return jsonify({
            "message": "Message received",
            "message_id": message_id,
            "sentiment": data.get('sentiment', data.get('emotion', 'unknown')),
            "total_messages": total_messages
        }), 201
    except Exception as e:
        return jsonify({"error": f"Failed to save message: {str(e)}"}), 500

@app.route('/messages', methods=['GET'])
def get_all_messages():
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        # Get query parameters for pagination and filtering
        limit = request.args.get('limit', type=int)
        skip = request.args.get('skip', type=int)
        source = request.args.get('source')
        sender = request.args.get('sender')
        sentiment = request.args.get('sentiment')
        
        if source:
            messages = db_manager.get_messages_by_source(source, limit)
        elif sender:
            messages = db_manager.get_messages_by_sender(sender, limit)
        elif sentiment:
            messages = db_manager.get_messages_by_sentiment(sentiment, limit)
        else:
            messages = db_manager.get_all_messages(limit=limit, skip=skip)
        
        return jsonify({
            "messages": messages,
            "total_count": db_manager.get_message_count()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve messages: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify database connectivity"""
    if not db_manager:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 503
    
    try:
        # Test database connection
        count = db_manager.get_message_count()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "message_count": count
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }), 503

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get basic statistics about the messages"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        total_messages = db_manager.get_message_count()
        
        # Get counts by source
        email_count = len(db_manager.get_messages_by_source('email'))
        chat_count = len(db_manager.get_messages_by_source('chat'))
        ticket_count = len(db_manager.get_messages_by_source('ticket'))
        
        # Get sentiment distribution
        sentiment_stats = db_manager.get_sentiment_stats()
        
        return jsonify({
            "total_messages": total_messages,
            "by_source": {
                "email": email_count,
                "chat": chat_count,
                "ticket": ticket_count
            },
            "by_sentiment": sentiment_stats
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get stats: {str(e)}"}), 500

@app.route('/sentiment/<sentiment_type>', methods=['GET'])
def get_messages_by_sentiment(sentiment_type):
    """Get messages filtered by specific sentiment"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        limit = request.args.get('limit', type=int)
        messages = db_manager.get_messages_by_sentiment(sentiment_type, limit)
        
        return jsonify({
            "sentiment": sentiment_type,
            "messages": messages,
            "count": len(messages)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get messages by sentiment: {str(e)}"}), 500

@app.route('/alerts', methods=['GET'])
def get_negative_sentiment_alerts():
    """Get messages with negative sentiment for monitoring"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        limit = request.args.get('limit', 10, type=int)
        negative_messages = db_manager.get_negative_sentiment_messages(limit)
        
        return jsonify({
            "alert_type": "negative_sentiment",
            "count": len(negative_messages),
            "messages": negative_messages
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get negative sentiment alerts: {str(e)}"}), 500

@app.route('/analyze', methods=['POST'])
def analyze_text_sentiment():
    """Analyze sentiment for any text without storing it"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400
    
    try:
        sentiment = classify_emotion_with_gemini(data['text'])
        return jsonify({
            "text": data['text'],
            "sentiment": sentiment,
            "analysis_only": True
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze sentiment: {str(e)}"}), 500

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Dashboard endpoint with comprehensive sentiment overview"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        # Get overall stats
        total_messages = db_manager.get_message_count()
        sentiment_stats = db_manager.get_sentiment_stats()
        
        # Get recent messages with sentiment
        recent_messages = db_manager.get_all_messages(limit=10)
        
        # Get negative sentiment alerts
        negative_alerts = db_manager.get_negative_sentiment_messages(limit=5)
        
        # Calculate sentiment distribution percentages
        sentiment_percentages = {}
        if total_messages > 0:
            for sentiment, count in sentiment_stats.items():
                sentiment_percentages[sentiment] = round((count / total_messages) * 100, 1)
        
        return jsonify({
            "dashboard": {
                "total_messages": total_messages,
                "sentiment_distribution": {
                    "counts": sentiment_stats,
                    "percentages": sentiment_percentages
                },
                "recent_messages": recent_messages,
                "negative_alerts": {
                    "count": len(negative_alerts),
                    "messages": negative_alerts
                }
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get dashboard data: {str(e)}"}), 500

@app.route('/api/emotion-overview', methods=['GET'])
def get_emotion_overview():
    """Get emotion overview data for dashboard cards with change percentages"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        # Get current period stats
        current_stats = db_manager.get_sentiment_stats()
        
        # Get previous period stats for comparison
        previous_stats = db_manager.get_sentiment_stats_comparison()
        
        # Map emotions to standard dashboard format
        emotion_mapping = {
            'angry': 'anger',
            'frustrated': 'anger',
            'furious': 'anger',
            'irritated': 'anger',
            'disgusted': 'anger',
            'upset': 'anger',
            'confused': 'confusion',
            'uncertain': 'confusion',
            'puzzled': 'confusion',
            'bewildered': 'confusion',
            'happy': 'joy',
            'joy': 'joy',
            'grateful': 'joy',
            'thrilled': 'joy',
            'delighted': 'joy',
            'pleased': 'joy',
            'satisfied': 'joy',
            'neutral': 'neutral',
            'unknown': 'neutral',
            'informational': 'neutral'
        }
        
        overview = {}
        
        # Standard emotion categories for dashboard
        dashboard_emotions = {
            'anger': {'count': 0, 'change_percent': 0},
            'joy': {'count': 0, 'change_percent': 0},
            'confusion': {'count': 0, 'change_percent': 0},
            'neutral': {'count': 0, 'change_percent': 0}
        }
        
        # Aggregate counts by mapped emotions
        for original_emotion, count in current_stats.items():
            mapped_emotion = emotion_mapping.get(original_emotion.lower(), 'neutral')
            dashboard_emotions[mapped_emotion]['count'] += count
        
        # Calculate total messages and actual percentages
        total_messages = sum(dashboard_emotions[emotion]['count'] for emotion in dashboard_emotions)
        
        for mapped_emotion in dashboard_emotions:
            current_count = dashboard_emotions[mapped_emotion]['count']
            
            # Calculate actual percentage of total messages
            if total_messages > 0:
                actual_percent = round((current_count / total_messages) * 100)
            else:
                actual_percent = 0
                
            dashboard_emotions[mapped_emotion]['change_percent'] = actual_percent
            dashboard_emotions[mapped_emotion]['total_messages'] = total_messages
            dashboard_emotions[mapped_emotion]['percentage_text'] = f"{current_count}/{total_messages} ({actual_percent}%)"
        
        return jsonify(dashboard_emotions)
    except Exception as e:
        return jsonify({"error": f"Failed to get emotion overview: {str(e)}"}), 500

@app.route('/api/emotion-trends', methods=['GET'])
def get_emotion_trends():
    """Get time-series data for emotion trends chart, optionally filtered by user"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        # Get time range and user filter from query params
        hours = request.args.get('hours', 6, type=int)
        user_id = request.args.get('user_id')
        
        # Get hourly emotion trends with optional user filtering
        trends_data = db_manager.get_hourly_emotion_trends(hours, user_id)
        
        # Convert dict to list of {time, ...}
        trends_list = [
            {"time": hour, **emotions}
            for hour, emotions in trends_data.items()
        ]
        
        response_data = {
            "trends": trends_list,
            "time_range_hours": hours
        }
        
        if user_id:
            response_data["user_id"] = user_id
            
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": f"Failed to get emotion trends: {str(e)}"}), 500

@app.route('/api/realtime-stats', methods=['GET'])
def get_realtime_stats():
    """Get real-time statistics for dashboard"""
    if not db_manager:
        return jsonify({"error": "Database connection not available"}), 500
    
    try:
        # Get stats for current hour
        current_hour_stats = db_manager.get_current_hour_stats()
        
        # Get total counts
        total_stats = db_manager.get_sentiment_stats()
        
        return jsonify({
            "current_hour": current_hour_stats,
            "total": total_stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get realtime stats: {str(e)}"}), 500

# Cleanup on app shutdown
@app.teardown_appcontext
def cleanup_db(error):
    pass

if __name__ == '__main__':
    try:
        # Get configuration from environment
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', '5000'))
        
        print(f"🚀 Starting server on {host}:{port} (debug={debug})")
        app.run(debug=debug, host=host, port=port)
    finally:
        if db_manager:
            db_manager.close_connection()
