# gemini_emotion_classifier.py
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
EMOTION_WORDS = [
    'angry', 'frustrated', 'happy', 'grateful', 'confused', 'uncertain', 'neutral',
    'joy', 'thrilled', 'delighted', 'upset', 'disgusted', 'irritated', 'furious',
    'puzzled'
]

ANGRY_KEYWORDS = [
    'angry', 'furious', 'frustrated', 'hate', 'terrible', 'awful', 'disgusting',
    'unacceptable', 'outrageous', 'livid', 'fed up', 'disgusted', 'irritated',
    'garbage', 'useless', 'worst', 'horrible', 'mad', 'pissed', 'annoyed'
]

HAPPY_KEYWORDS = [
    'thank you', 'grateful', 'happy', 'excellent', 'amazing', 'wonderful',
    'fantastic', 'great', 'love', 'thrilled', 'delighted', 'pleased',
    'satisfied', 'outstanding', 'perfect', 'brilliant', 'awesome'
]

CONFUSED_KEYWORDS = [
    'confused', 'don\'t understand', 'unclear', 'puzzled', 'uncertain',
    'not sure', 'bewildered', 'help me understand', 'clarify', 'explain'
]

# Get API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY environment variable is not set. "
        "Please add it to your .env file or set it as an environment variable."
    )

genai.configure(api_key=GOOGLE_API_KEY)


def classify_emotion_with_gemini(text):
    """
    Classify emotion using Gemini AI with fallback to keyword-based classification
    
    Args:
        text (str): The customer message to classify
        
    Returns:
        str: The detected emotion word
    """
    # First try Gemini AI
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"What is the emotional tone of this customer message? Return only one word from: {', '.join(EMOTION_WORDS[:7])}.\n\nMessage:\n{text}"
        
        response = model.generate_content(prompt)
        emotion = response.text.strip().lower()
        
        logger.info(f"🔍 Gemini raw response: '{response.text}'")
        logger.info(f"🔍 Processed emotion: '{emotion}'")
        
        # First try exact match
        for word in EMOTION_WORDS:
            if word == emotion:
                logger.info(f"✅ Exact match found: {word}")
                return word
        
        # Then try partial match (in case Gemini added extra text)
        for word in EMOTION_WORDS:
            if word in emotion:
                logger.info(f"✅ Partial match found: {word} in '{emotion}'")
                return word
                
        logger.warning(f"⚠️ No emotion word found in response, returning neutral")
        return 'neutral'
        
    except Exception as e:
        logger.error(f"❌ Gemini API error: {e}")
        # Fallback to keyword-based classification
        return classify_emotion_by_keywords(text)


def classify_emotion_by_keywords(text):
    """
    Fallback keyword-based emotion classification when Gemini API is unavailable
    
    Args:
        text (str): The customer message to classify
        
    Returns:
        str: The detected emotion word
    """
    text_lower = text.lower()
    logger.info(f"🔍 Fallback classifier analyzing: '{text}'")
    
    # Count keyword matches
    angry_score = sum(1 for keyword in ANGRY_KEYWORDS if keyword in text_lower)
    happy_score = sum(1 for keyword in HAPPY_KEYWORDS if keyword in text_lower)
    confused_score = sum(1 for keyword in CONFUSED_KEYWORDS if keyword in text_lower)
    
    logger.info(f"📊 Keyword scores - Angry: {angry_score}, Happy: {happy_score}, Confused: {confused_score}")
    
    # Determine emotion based on highest score
    if happy_score > 0 and happy_score >= angry_score and happy_score >= confused_score:
        logger.info(f"✅ Classified as: happy")
        return 'happy'
    elif angry_score > 0 and angry_score >= confused_score:
        logger.info(f"✅ Classified as: angry")
        return 'angry'
    elif confused_score > 0:
        logger.info(f"✅ Classified as: confused")
        return 'confused'
    else:
        logger.info(f"✅ Classified as: neutral")
        return 'neutral'
