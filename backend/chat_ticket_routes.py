from flask import Blueprint, request, jsonify
from datetime import datetime
from pymongo import MongoClient
import os

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["sentiment_customer"]

chat_collection = db["chat_messages"]
ticket_collection = db["tickets"]

# Create Blueprint
chat_ticket_bp = Blueprint("chat_ticket", __name__)
@chat_ticket_bp.route("/api/chat", methods=["POST"])
def save_chat():
    data = request.get_json()
    if not data or "user" not in data or "message" not in data:
        return jsonify({"error": "Invalid chat data"}), 400

    chat_doc = {
        "user": data["user"],
        "message": data["message"],
        "timestamp": datetime.utcnow(),
        "sentiment": None
    }
    chat_collection.insert_one(chat_doc)
    return jsonify({"status": "success", "data": chat_doc}), 201

@chat_ticket_bp.route("/api/ticket", methods=["POST"])
def save_ticket():
    data = request.get_json()
    if not data or "subject" not in data or "description" not in data:
        return jsonify({"error": "Invalid ticket data"}), 400

    ticket_doc = {
        "user": data.get("user", "Anonymous"),
        "subject": data["subject"],
        "description": data["description"],
        "priority": data.get("priority", "low"),
        "timestamp": datetime.utcnow(),
        "sentiment": None
    }
    ticket_collection.insert_one(ticket_doc)
    return jsonify({"status": "success", "data": ticket_doc}), 201

