# gemini_emotion_classifier.py
import google.generativeai as genai
import re

genai.configure(api_key="AIzaSyDEDaaFdyyJkRFXOVkLnIObAOr97WGGMtE")

def classify_emotion_with_gemini(text):
    """
    Classify emotion using Gemini AI with fallback to keyword-based classification
    """
    # First try Gemini AI
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"What is the emotional tone of this customer message? Return only one word from: angry, frustrated, happy, grateful, confused, uncertain, neutral.\n\nMessage:\n{text}"
        
        response = model.generate_content(prompt)
        emotion = response.text.strip().lower()
        
        print(f"🔍 Gemini raw response: '{response.text}'")
        print(f"🔍 Processed emotion: '{emotion}'")
        
        # Clean up the response (remove any extra text)
        emotion_words = ['angry', 'frustrated', 'happy', 'grateful', 'confused', 'uncertain', 'neutral', 'joy', 'thrilled', 'delighted', 'upset', 'disgusted', 'irritated', 'furious', 'puzzled', 'bewildered']
        
        # First try exact match
        for word in emotion_words:
            if word == emotion:
                print(f"✅ Exact match found: {word}")
                return word
        
        # Then try partial match (in case Gemini added extra text)
        for word in emotion_words:
            if word in emotion:
                print(f"✅ Partial match found: {word} in '{emotion}'")
                return word
                
        print(f"⚠️ No emotion word found in response, returning neutral")
        return 'neutral'
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        # Fallback to keyword-based classification
        return classify_emotion_by_keywords(text)

def classify_emotion_by_keywords(text):
    """
    Fallback keyword-based emotion classification when Gemini API is unavailable
    """
    text_lower = text.lower()
    print(f"🔍 Fallback classifier analyzing: '{text}'")
    
    # Negative/Angry keywords
    angry_keywords = [
        'angry', 'furious', 'frustrated', 'hate', 'terrible', 'awful', 'disgusting',
        'unacceptable', 'outrageous', 'livid', 'fed up', 'disgusted', 'irritated',
        'garbage', 'useless', 'worst', 'horrible', 'mad', 'pissed', 'annoyed'
    ]
    
    # Happy/Joy keywords
    happy_keywords = [
        'thank you', 'grateful', 'happy', 'excellent', 'amazing', 'wonderful',
        'fantastic', 'great', 'love', 'thrilled', 'delighted', 'pleased',
        'satisfied', 'outstanding', 'perfect', 'brilliant', 'awesome'
    ]
    
    # Confused keywords
    confused_keywords = [
        'confused', 'don\'t understand', 'unclear', 'puzzled', 'uncertain',
        'not sure', 'bewildered', 'help me understand', 'clarify', 'explain'
    ]
    
    # Count keyword matches
    angry_score = sum(1 for keyword in angry_keywords if keyword in text_lower)
    happy_score = sum(1 for keyword in happy_keywords if keyword in text_lower)
    confused_score = sum(1 for keyword in confused_keywords if keyword in text_lower)
    
    print(f"📊 Keyword scores - Angry: {angry_score}, Happy: {happy_score}, Confused: {confused_score}")
    
    # Determine emotion based on highest score (FIXED LOGIC)
    if happy_score > 0 and happy_score >= angry_score and happy_score >= confused_score:
        print(f"✅ Classified as: happy")
        return 'happy'
    elif angry_score > 0 and angry_score >= confused_score:
        print(f"✅ Classified as: angry")
        return 'angry'
    elif confused_score > 0:
        print(f"✅ Classified as: confused")
        return 'confused'
    else:
        print(f"✅ Classified as: neutral")
        return 'neutral'
