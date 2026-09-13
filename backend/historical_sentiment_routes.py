# historical_sentiment_routes.py
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from database import get_database_manager
from chat_ticket_sentiment_analyzer import analyze_chat_ticket_sentiment, get_detailed_sentiment
from dateutil import parser as date_parser
import os

historical_sentiment_bp = Blueprint("historical_sentiment", __name__)

db_manager = None
try:
    db_manager = get_database_manager()
    print("✅ DatabaseManager initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize DatabaseManager: {e}")


@historical_sentiment_bp.route('/api/historical/analyze-missing', methods=['POST'])
def analyze_missing_sentiments():
    """Backfill sentiment for existing chat/ticket documents without sentiment"""
    if db_manager is None:
        return jsonify({"error": "Database connection not available"}), 500

    try:
        # Get collections
        try:
            chat_coll = db_manager.db.get_collection('chat_messages')
            tix_coll = db_manager.db.get_collection('tickets')
            collections = [chat_coll, tix_coll]
        except Exception as e:
            print(f"❌ Error getting collections: {e}")
            return jsonify({"error": "Failed to access database collections"}), 500

        processed = {"updated": 0, "errors": 0}

        for coll in collections:
            if coll is None:
                continue

            try:
                # Find documents without sentiment or with invalid sentiment
                query = {
                    "$or": [
                        {"sentiment": {"$exists": False}},
                        {"sentiment": None},
                        {"sentiment": {"$in": ["none", "unknown", "informational", ""]}}
                    ]
                }

                documents_to_process = list(coll.find(query))
                print(f"📝 Processing {len(documents_to_process)} documents from {coll.name}")

                for doc in documents_to_process:
                    try:
                        # Extract text based on document type
                        text = ""
                        if 'message' in doc:
                            text = doc.get('message', '').strip()
                        elif 'description' in doc:
                            subject = doc.get('subject', '').strip()
                            description = doc.get('description', '').strip()
                            text = f"{subject} {description}".strip()

                        if not text:
                            print(f"⚠️ Empty text for document {doc.get('_id')}")
                            continue

                        # Classify sentiment using new analyzer
                        sentiment = analyze_chat_ticket_sentiment(text)

                        # Update document
                        coll.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"sentiment": sentiment}}
                        )
                        processed["updated"] += 1

                        if processed["updated"] % 10 == 0:
                            print(f"📊 Processed {processed['updated']} documents so far...")

                    except Exception as e:
                        print(f"❌ Error processing document {doc.get('_id')}: {e}")
                        processed["errors"] += 1

            except Exception as e:
                print(f"❌ Error processing collection {coll.name}: {e}")
                processed["errors"] += 1

        print(f"🎯 Backfill completed: {processed['updated']} updated, {processed['errors']} errors")
        return jsonify({"status": "completed", **processed})

    except Exception as e:
        print(f"❌ Failed to backfill sentiments: {str(e)}")
        return jsonify({"error": f"Failed to backfill sentiments: {str(e)}"}), 500


@historical_sentiment_bp.route('/api/historical/overview', methods=['GET'])
def historical_overview():
    """Aggregate sentiment across chat_messages and tickets"""
    if db_manager is None:
        return jsonify({"error": "Database connection not available"}), 500

    try:
        # Get collections
        chat_coll = db_manager.db.get_collection('chat_messages')
        tix_coll = db_manager.db.get_collection('tickets')

        if chat_coll is None or tix_coll is None:
            return jsonify({"error": "Collections not found"}), 500

        def fetch_all(coll):
            try:
                return list(coll.find({}))
            except Exception as e:
                print(f"❌ Error fetching from {coll.name}: {e}")
                return []

        # Fetch all documents
        chat_docs = fetch_all(chat_coll)
        tix_docs = fetch_all(tix_coll)
        all_docs = chat_docs + tix_docs

        print(f"📊 Found {len(all_docs)} total documents ({len(chat_docs)} chats, {len(tix_docs)} tickets)")

        # Count sentiments and classify missing ones
        sentiment_counts = {}
        classification_count = 0

        for doc in all_docs:
            try:
                # Extract text
                text = ""
                if 'message' in doc:
                    text = doc.get('message', '').strip()
                elif 'description' in doc:
                    subject = doc.get('subject', '').strip()
                    description = doc.get('description', '').strip()
                    text = f"{subject} {description}".strip()

                if not text:
                    continue

                sentiment = doc.get("sentiment", "").lower() if doc.get("sentiment") else ""

                # Classify if sentiment is missing or invalid
                if not sentiment or sentiment in ["none", "unknown", "informational", ""]:
                    print(f"🔍 Classifying text: '{text[:50]}...'")
                    sentiment = analyze_chat_ticket_sentiment(text)
                    print(f"✅ Classification result: {sentiment}")
                    classification_count += 1

                    # Update the document in database
                    coll = chat_coll if 'message' in doc else tix_coll
                    try:
                        coll.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"sentiment": sentiment}}
                        )
                    except Exception as e:
                        print(f"⚠️ Could not update document {doc['_id']}: {e}")

                # Count the sentiment
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

            except Exception as e:
                print(f"❌ Error processing document: {e}")
                continue

        print(f"🎯 Classified {classification_count} documents, sentiment counts: {sentiment_counts}")

        # Map to dashboard categories with fallback
        emotion_mapping = {
            'angry': 'anger', 'frustrated': 'anger', 'furious': 'anger',
            'irritated': 'anger', 'disgusted': 'anger', 'upset': 'anger',
            'confused': 'confusion', 'uncertain': 'confusion',
            'puzzled': 'confusion', 'bewildered': 'confusion',
            'happy': 'joy', 'joy': 'joy', 'grateful': 'joy',
            'thrilled': 'joy', 'delighted': 'joy', 'pleased': 'joy',
            'satisfied': 'joy',
            'neutral': 'neutral', 'unknown': 'neutral', 'informational': 'neutral'
        }

        dashboard = {
            'anger': {'count': 0},
            'confusion': {'count': 0},
            'joy': {'count': 0},
            'neutral': {'count': 0}
        }

        for sentiment, count in sentiment_counts.items():
            sentiment_lower = str(sentiment).lower()
            
            # First try direct match (new analyzer returns dashboard categories)
            if sentiment_lower in dashboard:
                dashboard[sentiment_lower]['count'] += count
            else:
                # Fallback to emotion mapping (old analyzer or unexpected results)
                mapped = emotion_mapping.get(sentiment_lower, 'neutral')
                dashboard[mapped]['count'] += count

        total = sum(v['count'] for v in dashboard.values())
        if total == 0:
            total = 1  # Avoid division by zero

        for key in dashboard:
            pct = round((dashboard[key]['count'] / total) * 100)
            dashboard[key]['percentage_text'] = f"{dashboard[key]['count']}/{total} ({pct}%)"

        return jsonify(dashboard)

    except Exception as e:
        print(f"❌ Error in historical_overview: {str(e)}")
        return jsonify({"error": f"Failed to get overview: {str(e)}"}), 500


@historical_sentiment_bp.route('/api/historical/trends', methods=['GET'])
def historical_trends():
    """Hourly emotion trends using chat_messages and tickets"""
    if db_manager is None:
        return jsonify({"error": "Database connection not available"}), 500

    try:
        hours = request.args.get('hours', 12, type=int)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        # Get collections
        chat_coll = db_manager.db.get_collection('chat_messages')
        tix_coll = db_manager.db.get_collection('tickets')

        if chat_coll is None or tix_coll is None:
            return jsonify({"error": "Collections not found"}), 500

        def fetch_docs(coll):
            try:
                return list(coll.find({
                    "timestamp": {
                        "$gte": start_time,
                        "$lt": end_time
                    }
                }))
            except Exception as e:
                print(f"❌ Error fetching time-based docs from {coll.name}: {e}")
                return []

        chat_docs = fetch_docs(chat_coll)
        tix_docs = fetch_docs(tix_coll)
        all_docs = chat_docs + tix_docs

        print(f"📈 Found {len(all_docs)} documents in the last {hours} hours")

        # Build hourly buckets
        from collections import OrderedDict
        buckets = OrderedDict()
        cursor = start_time.replace(minute=0, second=0, microsecond=0)

        while cursor <= end_time:
            hour_key = cursor.strftime("%H:00")
            buckets[hour_key] = {'anger': 0, 'confusion': 0, 'joy': 0, 'neutral': 0}
            cursor += timedelta(hours=1)

        # Map to dashboard categories with fallback
        emotion_mapping = {
            'angry': 'anger', 'frustrated': 'anger', 'furious': 'anger',
            'irritated': 'anger', 'disgusted': 'anger', 'upset': 'anger',
            'confused': 'confusion', 'uncertain': 'confusion',
            'puzzled': 'confusion', 'bewildered': 'confusion',
            'happy': 'joy', 'joy': 'joy', 'grateful': 'joy',
            'thrilled': 'joy', 'delighted': 'joy', 'pleased': 'joy',
            'satisfied': 'joy',
            'neutral': 'neutral', 'unknown': 'neutral', 'informational': 'neutral'
        }

        for doc in all_docs:
            try:
                # Parse timestamp
                ts = doc.get('timestamp')
                if isinstance(ts, str):
                    ts = date_parser.parse(ts)

                if not isinstance(ts, datetime):
                    continue

                hour_key = ts.strftime("%H:00")
                if hour_key not in buckets:
                    continue

                # Extract text
                text = ""
                if 'message' in doc:
                    text = doc.get('message', '').strip()
                elif 'description' in doc:
                    subject = doc.get('subject', '').strip()
                    description = doc.get('description', '').strip()
                    text = f"{subject} {description}".strip()

                if not text:
                    continue

                sentiment = doc.get("sentiment", "").lower() if doc.get("sentiment") else ""

                # Classify if needed
                if not sentiment or sentiment in ["none", "unknown", "informational", ""]:
                    print(f"🔍 Classifying text for trends: '{text[:50]}...'")
                    sentiment = analyze_chat_ticket_sentiment(text)
                    print(f"✅ Trends classification result: {sentiment}")

                    # Update the document
                    coll = chat_coll if 'message' in doc else tix_coll
                    try:
                        coll.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"sentiment": sentiment}}
                        )
                    except Exception as e:
                        print(f"⚠️ Could not update document {doc['_id']}: {e}")

                # Map sentiment to dashboard category with fallback
                sentiment_lower = str(sentiment).lower()
                
                # First try direct match (new analyzer returns dashboard categories)
                if sentiment_lower in buckets[hour_key]:
                    buckets[hour_key][sentiment_lower] += 1
                else:
                    # Fallback to emotion mapping (old analyzer or unexpected results)
                    mapped = emotion_mapping.get(sentiment_lower, 'neutral')
                    buckets[hour_key][mapped] += 1

            except Exception as e:
                print(f"❌ Error processing trend document: {e}")
                continue

        trends_list = [{"time": k, **v} for k, v in buckets.items()]
        return jsonify({"trends": trends_list, "time_range_hours": hours})

    except Exception as e:
        print(f"❌ Error in historical_trends: {str(e)}")
        return jsonify({"error": f"Failed to get trends: {str(e)}"}), 500


@historical_sentiment_bp.route('/api/historical/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check database status"""
    if db_manager is None:
        return jsonify({"status": "database_not_connected"})

    try:
        chat_coll = db_manager.db.get_collection('chat_messages')
        tix_coll = db_manager.db.get_collection('tickets')

        chat_count = chat_coll.count_documents({}) if chat_coll else 0
        tix_count = tix_coll.count_documents({}) if tix_coll else 0

        # Count documents with different sentiment values
        sentiment_stats = {}
        for coll in [chat_coll, tix_coll]:
            if coll:
                pipeline = [
                    {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
                ]
                stats = list(coll.aggregate(pipeline))
                for stat in stats:
                    sentiment = stat['_id'] or 'none'
                    sentiment_stats[sentiment] = sentiment_stats.get(sentiment, 0) + stat['count']

        return jsonify({
            "status": "connected",
            "chat_messages_count": chat_count,
            "tickets_count": tix_count,
            "total_documents": chat_count + tix_count,
            "sentiment_stats": sentiment_stats,
            "gemini_api_key_set": bool(os.getenv('GEMINI_API_KEY'))
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@historical_sentiment_bp.route('/api/historical/test-analyzer', methods=['POST'])
def test_sentiment_analyzer():
    """Test the new sentiment analyzer with sample text"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Please provide 'text' in request body"}), 400
        
        text = data['text']
        
        # Get both simple and detailed analysis
        simple_sentiment = analyze_chat_ticket_sentiment(text)
        detailed_analysis = get_detailed_sentiment(text)
        
        return jsonify({
            "text": text,
            "simple_sentiment": simple_sentiment,
            "detailed_analysis": detailed_analysis
        })
        
    except Exception as e:
        return jsonify({"error": f"Test failed: {str(e)}"}), 500