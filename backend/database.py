import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.messages = None
        self.alerts = None
        self.analytics = None
        self.users = None
        self.settings = None
        self.history = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            # Get connection details from environment
            mongodb_uri = os.getenv('MONGODB_URI')
            database_name = os.getenv('DATABASE_NAME', 'sentiment_sentinel')
            collection_name = os.getenv('COLLECTION_NAME', 'messages')
            
            if not mongodb_uri:
                raise ValueError("MONGODB_URI not found in environment variables")
            
            # Create MongoDB client
            self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            
            # Test the connection
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB!")
            
            # Get database and collections
            self.db = self.client[database_name]
            self.messages = self.db['messages']
            self.alerts = self.db['alerts']
            self.analytics = self.db['sentiment_analytics'] 
            self.users = self.db['users']
            self.settings = self.db['settings']
            self.history = self.db['sentiment_history']
            self.email_configs = self.db['email_configs']  # New collection for email configurations
            
            # Maintain backward compatibility
            self.collection = self.messages
            
            # Create indexes for better performance
            self.create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Messages collection indexes
            self.messages.create_index("timestamp")
            self.messages.create_index("source")
            self.messages.create_index("sender")
            self.messages.create_index("sentiment")
            self.messages.create_index("emotion")
            self.messages.create_index([("source", 1), ("timestamp", -1)])
            self.messages.create_index([("sentiment", 1), ("timestamp", -1)])
            
            # Alerts collection indexes (if not already created)
            self.alerts.create_index("message_id")
            self.alerts.create_index("alert_type")
            self.alerts.create_index("status")
            
            print("✅ Database indexes verified successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    def insert_message(self, message_data):
        """Insert a single message into the database"""
        try:
            # Add created_at timestamp if not present
            if 'created_at' not in message_data:
                message_data['created_at'] = message_data.get('timestamp')
            
            # Add normalized timestamp for better querying
            if 'timestamp' in message_data and isinstance(message_data['timestamp'], str):
                try:
                    from dateutil import parser as date_parser
                    parsed_time = date_parser.parse(message_data['timestamp'])
                    message_data['timestamp_parsed'] = parsed_time
                    message_data['timestamp_iso'] = parsed_time.isoformat()
                except Exception as e:
                    print(f"⚠️ Could not parse timestamp: {e}")
                    message_data['timestamp_parsed'] = datetime.now()
                    message_data['timestamp_iso'] = datetime.now().isoformat()
            else:
                message_data['timestamp_parsed'] = datetime.now()
                message_data['timestamp_iso'] = datetime.now().isoformat()
            
            # Add status if not present
            if 'status' not in message_data:
                message_data['status'] = 'new'
            
            # Set priority based on sentiment
            if 'priority' not in message_data:
                sentiment = message_data.get('sentiment', message_data.get('emotion', '')).lower()
                negative_sentiments = ['angry', 'frustrated', 'upset', 'disappointed', 'furious', 'irritated']
                if sentiment in negative_sentiments:
                    message_data['priority'] = 'high'
                elif sentiment in ['confused', 'concerned', 'worried']:
                    message_data['priority'] = 'medium'
                else:
                    message_data['priority'] = 'low'
            
            result = self.messages.insert_one(message_data)
            
            # Create alert if negative sentiment
            self._check_and_create_alert(message_data, str(result.inserted_id))
            
            # Save sentiment history for tracking
            sentiment = message_data.get('sentiment', message_data.get('emotion'))
            if sentiment:
                try:
                    self.save_sentiment_history(message_data, sentiment)
                except Exception as e:
                    print(f"⚠️ Warning: Could not save sentiment history: {e}")
            
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error inserting message: {e}")
            raise
    
    def get_all_messages(self, limit=None, skip=None, sort_by="timestamp", sort_order=-1):
        """Retrieve messages from database with optional pagination and sorting"""
        try:
            cursor = self.messages.find()
            
            # Apply sorting
            cursor = cursor.sort(sort_by, sort_order)
            
            # Apply pagination
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            # Convert to list and handle ObjectId serialization
            messages = []
            for message in cursor:
                message['_id'] = str(message['_id'])  # Convert ObjectId to string
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"❌ Error retrieving messages: {e}")
            raise
    
    def get_message_count(self):
        """Get total count of messages in database"""
        try:
            return self.messages.count_documents({})
        except Exception as e:
            print(f"❌ Error getting message count: {e}")
            raise
    
    def get_messages_by_source(self, source, limit=None):
        """Get messages filtered by source (email, chat, ticket)"""
        try:
            cursor = self.messages.find({"source": source}).sort("timestamp", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            messages = []
            for message in cursor:
                message['_id'] = str(message['_id'])
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"❌ Error getting messages by source: {e}")
            raise
    
    def get_messages_by_sender(self, sender, limit=None):
        """Get messages filtered by sender"""
        try:
            cursor = self.messages.find({"sender": sender}).sort("timestamp", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            messages = []
            for message in cursor:
                message['_id'] = str(message['_id'])
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"❌ Error getting messages by sender: {e}")
            raise
    
    def get_messages_by_sentiment(self, sentiment, limit=None):
        """Get messages filtered by sentiment/emotion"""
        try:
            # Search both 'sentiment' and 'emotion' fields for compatibility
            cursor = self.messages.find({
                "$or": [
                    {"sentiment": sentiment},
                    {"emotion": sentiment}
                ]
            }).sort("timestamp", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            messages = []
            for message in cursor:
                message['_id'] = str(message['_id'])
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"❌ Error getting messages by sentiment: {e}")
            raise
    
    def get_sentiment_stats(self):
        """Get sentiment distribution statistics"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": {"$ifNull": ["$sentiment", "$emotion"]},
                        "count": {"$sum": 1}
                    }
                },
                {"$match": {"_id": {"$ne": None}}}
            ]
            
            results = list(self.messages.aggregate(pipeline))
            sentiment_counts = {result["_id"]: result["count"] for result in results}
            
            return sentiment_counts
        except Exception as e:
            print(f"❌ Error getting sentiment stats: {e}")
            return {}

    def get_sentiment_stats_comparison(self, hours_ago=24):
        """Get sentiment stats from previous period for comparison"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate timestamp for comparison period
            cutoff_time = datetime.now() - timedelta(hours=hours_ago)
            
            pipeline = [
                {
                    "$match": {
                        "created_at": {"$lt": cutoff_time.isoformat()}
                    }
                },
                {
                    "$group": {
                        "_id": {"$ifNull": ["$sentiment", "$emotion"]},
                        "count": {"$sum": 1}
                    }
                },
                {"$match": {"_id": {"$ne": None}}}
            ]
            
            results = list(self.messages.aggregate(pipeline))
            sentiment_counts = {result["_id"]: result["count"] for result in results}
            
            return sentiment_counts
        except Exception as e:
            print(f"❌ Error getting sentiment stats comparison: {e}")
            return {}

    def get_hourly_emotion_trends(self, hours=6, user_id=None):
        """Get hourly emotion trends for the specified number of hours, optionally filtered by user"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Generate hourly buckets
            hourly_data = {}
            current_time = start_time
            
            while current_time <= end_time:
                hour_key = current_time.strftime("%H:%M")
                next_hour = current_time + timedelta(hours=1)
                
                # Build query for this hour
                query = {
                    "$or": [
                        {"timestamp_parsed": {"$gte": current_time, "$lt": next_hour}},
                        {"timestamp_iso": {"$gte": current_time.isoformat(), "$lt": next_hour.isoformat()}}
                    ]
                }
                
                # Add user filter if specified
                if user_id:
                    query["user_id"] = user_id
                
                # Try to use optimized query first
                try:
                    hour_messages = list(self.messages.find(query))
                except Exception:
                    # Fallback to Python filtering for backward compatibility
                    print(f"⚠️ Using fallback filtering for hour {hour_key}")
                    hour_messages = []
                    
                    # Get all messages and filter by timestamp in Python
                    base_query = {"user_id": user_id} if user_id else {}
                    all_messages_cursor = self.messages.find(base_query)
                    
                    for msg in all_messages_cursor:
                        msg_timestamp_str = msg.get('timestamp_iso') or msg.get('timestamp') or msg.get('created_at')
                        if msg_timestamp_str:
                            try:
                                # Parse timestamp string to datetime object
                                if isinstance(msg_timestamp_str, str):
                                    from dateutil import parser as date_parser
                                    msg_timestamp = date_parser.parse(msg_timestamp_str)
                                else:
                                    msg_timestamp = msg_timestamp_str
                                
                                # Check if message falls within current hour
                                if current_time <= msg_timestamp < next_hour:
                                    hour_messages.append(msg)
                            except Exception:
                                # Skip messages with invalid timestamps
                                continue
                
                # Count emotions for this hour using improved mapping
                emotion_counts = {'anger': 0, 'confusion': 0, 'joy': 0, 'neutral': 0}
                
                emotion_mapping = {
                    'angry': 'anger',
                    'frustrated': 'anger',
                    'furious': 'anger',
                    'irritated': 'anger',
                    'disgusted': 'anger',
                    'upset': 'anger',
                    'livid': 'anger',
                    'mad': 'anger',
                    'confused': 'confusion',
                    'uncertain': 'confusion',
                    'puzzled': 'confusion',
                    'bewildered': 'confusion',
                    'unclear': 'confusion',
                    'happy': 'joy',
                    'joy': 'joy',
                    'grateful': 'joy',
                    'thrilled': 'joy',
                    'delighted': 'joy',
                    'pleased': 'joy',
                    'satisfied': 'joy',
                    'excellent': 'joy',
                    'amazing': 'joy',
                    'wonderful': 'joy',
                    'fantastic': 'joy',
                    'great': 'joy',
                    'outstanding': 'joy',
                    'neutral': 'neutral',
                    'unknown': 'neutral',
                    'informational': 'neutral'
                }
                
                for msg in hour_messages:
                    emotion = msg.get('sentiment', msg.get('emotion', 'neutral')).lower()
                    mapped_emotion = emotion_mapping.get(emotion, 'neutral')
                    emotion_counts[mapped_emotion] += 1
                
                hourly_data[hour_key] = emotion_counts
                current_time = next_hour
            
            return hourly_data
        except Exception as e:
            print(f"❌ Error getting hourly emotion trends: {e}")
            return {}

    def get_current_hour_stats(self):
        """Get emotion statistics for the current hour"""
        try:
            from datetime import timedelta
            
            now = datetime.now()
            current_hour_start = now.replace(minute=0, second=0, microsecond=0)
            next_hour = current_hour_start + timedelta(hours=1)
            
            # Query messages for current hour
            current_hour_messages = list(self.messages.find({
                "created_at": {
                    "$gte": current_hour_start.isoformat(),
                    "$lt": next_hour.isoformat()
                }
            }))
            
            # Count emotions
            emotion_counts = {'anger': 0, 'confusion': 0, 'joy': 0, 'neutral': 0}
            
            for msg in current_hour_messages:
                emotion = msg.get('sentiment', msg.get('emotion', 'neutral')).lower()
                if emotion in ['angry', 'frustrated', 'upset']:
                    emotion_counts['anger'] += 1
                elif emotion in ['confused', 'uncertain']:
                    emotion_counts['confusion'] += 1
                elif emotion in ['happy', 'joy', 'satisfied']:
                    emotion_counts['joy'] += 1
                else:
                    emotion_counts['neutral'] += 1
            
            return emotion_counts
        except Exception as e:
            print(f"❌ Error getting current hour stats: {e}")
            return {'anger': 0, 'confusion': 0, 'joy': 0, 'neutral': 0}
    
    def get_negative_sentiment_messages(self, limit=None):
        """Get messages with negative sentiment (angry, frustrated, upset, etc.)"""
        try:
            negative_sentiments = ["angry", "frustrated", "upset", "disappointed", "annoyed", "furious", "irritated"]
            cursor = self.messages.find({
                "$or": [
                    {"sentiment": {"$in": negative_sentiments}},
                    {"emotion": {"$in": negative_sentiments}}
                ]
            }).sort("timestamp", -1)
            
            if limit:
                cursor = cursor.limit(limit)
            
            messages = []
            for message in cursor:
                message['_id'] = str(message['_id'])
                messages.append(message)
            
            return messages
        except Exception as e:
            print(f"❌ Error getting negative sentiment messages: {e}")
            raise
    
    def _check_and_create_alert(self, message_data, message_id):
        """Create alert for negative sentiment messages"""
        try:
            sentiment = message_data.get('sentiment', message_data.get('emotion', '')).lower()
            negative_sentiments = ['angry', 'frustrated', 'upset', 'disappointed', 'furious', 'irritated']
            
            if sentiment in negative_sentiments:
                alert_data = {
                    "message_id": message_data.get('id', message_id),
                    "alert_type": "negative_sentiment",
                    "severity": "high" if sentiment in ['angry', 'furious'] else "medium",
                    "sentiment": sentiment,
                    "description": f"Negative sentiment detected: {sentiment}",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                
                self.alerts.insert_one(alert_data)
                print(f"🚨 Alert created for negative sentiment: {sentiment}")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not create alert: {e}")
    
    def get_active_alerts(self, limit=None):
        """Get active alerts"""
        try:
            cursor = self.alerts.find({"status": "active"}).sort("created_at", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            alerts = []
            for alert in cursor:
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            return alerts
        except Exception as e:
            print(f"❌ Error getting active alerts: {e}")
            raise
    
    def get_settings(self, category=None):
        """Get system settings"""
        try:
            query = {"category": category} if category else {}
            settings = {}
            
            for setting in self.settings.find(query):
                settings[setting['key']] = setting['value']
            
            return settings
        except Exception as e:
            print(f"❌ Error getting settings: {e}")
            return {}
    
    def save_sentiment_history(self, message_data, sentiment, confidence_score=None, processing_time=None):
        """Save sentiment analysis history for tracking and ML training"""
        try:
            history_entry = {
                "message_id": message_data.get('id'),
                "timestamp": datetime.now().isoformat(),
                "original_text": message_data.get('text', '')[:200],  # First 200 chars
                "sentiment": sentiment,
                "confidence_score": confidence_score or 0.85,  # Default confidence
                "source": message_data.get('source', 'unknown'),
                "sender": message_data.get('sender', 'unknown'),
                "model_version": "gemini-1.5",
                "processing_time_ms": processing_time or 1200,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.history.insert_one(history_entry)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error saving sentiment history: {e}")
            raise
    
    def generate_weekly_analytics(self, week_start_date=None):
        """Generate and save weekly sentiment analytics"""
        try:
            from datetime import datetime, timedelta
            
            if not week_start_date:
                # Default to current week (Monday to Sunday)
                today = datetime.now()
                days_since_monday = today.weekday()
                week_start = today - timedelta(days=days_since_monday)
                week_start_date = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            week_end_date = week_start_date + timedelta(days=7)
            
            # Query messages from this week
            week_messages = list(self.messages.find({
                "created_at": {
                    "$gte": week_start_date.isoformat(),
                    "$lt": week_end_date.isoformat()
                }
            }))
            
            if not week_messages:
                print(f"No messages found for week starting {week_start_date.date()}")
                return None
            
            # Calculate analytics
            total_messages = len(week_messages)
            sentiment_counts = {}
            source_counts = {}
            daily_counts = {}
            priority_counts = {}
            
            for msg in week_messages:
                # Sentiment breakdown
                sentiment = msg.get('sentiment', msg.get('emotion', 'unknown'))
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                # Source breakdown
                source = msg.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
                
                # Priority breakdown
                priority = msg.get('priority', 'low')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                # Daily breakdown
                msg_date = msg.get('created_at', '')[:10]  # Get date part
                daily_counts[msg_date] = daily_counts.get(msg_date, 0) + 1
            
            # Get alerts for this week
            week_alerts = list(self.alerts.find({
                "created_at": {
                    "$gte": week_start_date.isoformat(),
                    "$lt": week_end_date.isoformat()
                }
            }))
            
            # Create weekly analytics document
            weekly_analytics = {
                "week_start": week_start_date.isoformat(),
                "week_end": week_end_date.isoformat(),
                "total_messages": total_messages,
                "sentiment_breakdown": sentiment_counts,
                "source_breakdown": source_counts,
                "priority_breakdown": priority_counts,
                "daily_message_counts": daily_counts,
                "total_alerts": len(week_alerts),
                "alert_breakdown": {
                    "high_priority": len([a for a in week_alerts if a.get('severity') == 'high']),
                    "medium_priority": len([a for a in week_alerts if a.get('severity') == 'medium'])
                },
                "average_messages_per_day": round(total_messages / 7, 2),
                "negative_sentiment_ratio": round(
                    sum(sentiment_counts.get(s, 0) for s in ['angry', 'frustrated', 'upset', 'disappointed']) / total_messages * 100, 2
                ) if total_messages > 0 else 0,
                "created_at": datetime.now().isoformat(),
                "report_type": "weekly_summary"
            }
            
            # Save to analytics collection
            result = self.analytics.insert_one(weekly_analytics)
            print(f"✅ Weekly analytics saved for week {week_start_date.date()}")
            print(f"📊 Total messages: {total_messages}, Alerts: {len(week_alerts)}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error generating weekly analytics: {e}")
            raise
    
    def generate_daily_analytics(self, target_date=None):
        """Generate and save daily sentiment analytics"""
        try:
            if not target_date:
                target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            next_day = target_date + timedelta(days=1)
            
            # Query messages from this day
            day_messages = list(self.messages.find({
                "created_at": {
                    "$gte": target_date.isoformat(),
                    "$lt": next_day.isoformat()
                }
            }))
            
            if not day_messages:
                print(f"No messages found for {target_date.date()}")
                return None
            
            # Calculate daily analytics similar to weekly
            total_messages = len(day_messages)
            sentiment_counts = {}
            source_counts = {}
            hourly_counts = {}
            
            for msg in day_messages:
                sentiment = msg.get('sentiment', msg.get('emotion', 'unknown'))
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                source = msg.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
                
                # Hourly breakdown
                msg_time = msg.get('created_at', '')
                if len(msg_time) >= 13:
                    hour = msg_time[11:13]  # Extract hour
                    hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            daily_analytics = {
                "date": target_date.date().isoformat(),
                "total_messages": total_messages,
                "sentiment_breakdown": sentiment_counts,
                "source_breakdown": source_counts,
                "hourly_breakdown": hourly_counts,
                "created_at": datetime.now().isoformat(),
                "report_type": "daily_summary"
            }
            
            result = self.analytics.insert_one(daily_analytics)
            print(f"✅ Daily analytics saved for {target_date.date()}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error generating daily analytics: {e}")
            raise
    
    def get_analytics_by_period(self, report_type="weekly", limit=10):
        """Get analytics reports by period (daily, weekly, monthly)"""
        try:
            cursor = self.analytics.find({"report_type": f"{report_type}_summary"}).sort("created_at", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            analytics = []
            for record in cursor:
                record['_id'] = str(record['_id'])
                analytics.append(record)
            
            return analytics
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            return []
    
    def get_sentiment_history(self, limit=None, message_id=None):
        """Get sentiment analysis history"""
        try:
            query = {"message_id": message_id} if message_id else {}
            cursor = self.history.find(query).sort("timestamp", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            history = []
            for record in cursor:
                record['_id'] = str(record['_id'])
                history.append(record)
            
            return history
        except Exception as e:
            print(f"❌ Error getting sentiment history: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("✅ Database connection closed")
    
    def save_email_config(self, config_data, user_id=None):
        """Save or update email configuration for a specific user or globally"""
        try:
            # Add timestamp
            config_data['updated_at'] = datetime.now().isoformat()
            config_data['created_at'] = config_data.get('created_at', datetime.now().isoformat())
            
            if user_id:
                # User-specific configuration
                result = self.email_configs.update_one(
                    {"user_id": user_id},  # Find config for specific user
                    {
                        "$set": {
                            **config_data,
                            "user_id": user_id,
                            "active": True
                        }
                    },
                    upsert=True
                )
            else:
                # Global configuration (backward compatibility)
                result = self.email_configs.update_one(
                    {"active": True, "user_id": {"$exists": False}},  # Find the global active configuration
                    {
                        "$set": {
                            **config_data,
                            "active": True
                        }
                    },
                    upsert=True
                )
            
            if result.upserted_id:
                return str(result.upserted_id)
            else:
                # Find and return the updated document's ID
                query = {"user_id": user_id} if user_id else {"active": True, "user_id": {"$exists": False}}
                existing = self.email_configs.find_one(query)
                return str(existing["_id"]) if existing else None
                
        except Exception as e:
            print(f"❌ Error saving email config: {e}")
            raise
    
    def get_email_config(self, user_id=None):
        """Get email configuration for a specific user or the global active configuration"""
        try:
            if user_id:
                # Get user-specific configuration
                config = self.email_configs.find_one({"user_id": user_id, "active": True})
            else:
                # Get global configuration (backward compatibility)
                config = self.email_configs.find_one({"active": True, "user_id": {"$exists": False}})
                
                # If no global config found, try to get any active config for backward compatibility
                if not config:
                    config = self.email_configs.find_one({"active": True})
            
            if config:
                # Convert ObjectId to string for JSON serialization
                config["_id"] = str(config["_id"])
                return config
            return None
        except Exception as e:
            print(f"❌ Error retrieving email config: {e}")
            raise
            
    def get_all_email_configs(self):
        """Get all active email configurations"""
        try:
            configs = list(self.email_configs.find({"active": True}))
            for config in configs:
                config["_id"] = str(config["_id"])
            return configs
        except Exception as e:
            print(f"❌ Error retrieving all email configs: {e}")
            raise

# Global database manager instance
db_manager = None

def get_database_manager():
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
