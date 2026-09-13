# Sentiment Sentinel AI Backend

## 🚀 Deployment Guide

### Environment Variables Required:
```
MONGODB_URI=mongodb+srv://your-connection-string
GEMINI_API_KEY=your-gemini-api-key
DATABASE_NAME=sentiment_sentinel
COLLECTION_NAME=messages
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### Local Development:
```bash
pip install -r requirements.txt
python app.py
```

### Production Deployment:

#### Option 1: Heroku
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set MONGODB_URI="your-connection-string"
heroku config:set GEMINI_API_KEY="your-api-key"
heroku config:set DATABASE_NAME="sentiment_sentinel" 
heroku config:set COLLECTION_NAME="messages"
heroku config:set FLASK_DEBUG="false"
git push heroku main
```

#### Option 2: Railway/Render
1. Connect GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically

#### Option 3: Docker
```bash
docker build -t sentiment-backend .
docker run -p 5000:5000 --env-file .env sentiment-backend
```

### API Endpoints Available:
- `GET /` - Health check
- `POST /message` - Submit new message
- `GET /messages` - Get all messages  
- `GET /dashboard` - Dashboard overview
- `GET /api/emotion-overview` - Emotion cards data
- `GET /api/emotion-trends` - Real-time trends
- `GET /api/realtime-stats` - Current statistics
- `GET /health` - System health check

### Frontend Integration:
Your frontend should call these endpoints. CORS is enabled for all origins.

Example frontend code:
```javascript
// Get dashboard data
const response = await fetch('https://your-backend-url.com/api/emotion-overview');
const data = await response.json();
console.log(data);
```
