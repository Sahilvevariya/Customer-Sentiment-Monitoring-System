# chat_ticket_sentiment_analyzer.py
import re
import os
from typing import Dict, List, Tuple

# Import Gemini classifier
try:
    from gemini_emotion_classifier import classify_emotion_with_gemini
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI integration available")
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"⚠️ Gemini AI not available: {e}")

class ChatTicketSentimentAnalyzer:
    """
    Dedicated sentiment analyzer for chat and ticket messages
    Uses Gemini AI when available, with pattern matching as fallback
    """
    
    def __init__(self):
        # Define emotion patterns with weights
        self.emotion_patterns = {
            'anger': {
                'high': [
                    r'\b(angry|furious|livid|enraged|outraged)\b',
                    r'\b(hate|loathe|despise|abhor)\b',
                    r'\b(terrible|awful|horrible|dreadful|atrocious)\b',
                    r'\b(useless|worthless|garbage|trash|rubbish)\b',
                    r'\b(fed up|sick of|tired of|had enough)\b',
                    r'\b(never|ever again|worst|disaster)\b'
                ],
                'medium': [
                    r'\b(frustrated|irritated|annoyed|bothered)\b',
                    r'\b(disappointed|dissatisfied|unhappy)\b',
                    r'\b(problem|issue|bug|error|fail)\b',
                    r'\b(slow|delayed|late|waiting)\b',
                    r'\b(expensive|costly|overpriced)\b',
                    r'\b(complicated|complex|difficult|hard)\b'
                ],
                'low': [
                    r'\b(not good|not great|not happy)\b',
                    r'\b(could be better|room for improvement)\b',
                    r'\b(concerned|worried|anxious)\b'
                ]
            },
            'joy': {
                'high': [
                    r'\b(excellent|outstanding|amazing|fantastic)\b',
                    r'\b(perfect|brilliant|superb|magnificent)\b',
                    r'\b(love|adore|cherish|treasure)\b',
                    r'\b(thrilled|delighted|ecstatic|overjoyed)\b',
                    r'\b(best|greatest|top|number one)\b'
                ],
                'medium': [
                    r'\b(happy|pleased|satisfied|content)\b',
                    r'\b(good|great|nice|wonderful)\b',
                    r'\b(thank you|thanks|grateful|appreciate)\b',
                    r'\b(working|fixed|resolved|solved)\b',
                    r'\b(fast|quick|efficient|smooth)\b',
                    r'\b(easy|simple|straightforward)\b'
                ],
                'low': [
                    r'\b(okay|fine|alright|acceptable)\b',
                    r'\b(not bad|decent|reasonable)\b',
                    r'\b(progress|improvement|better)\b'
                ]
            },
            'confusion': {
                'high': [
                    r'\b(completely lost|totally confused|no idea)\b',
                    r'\b(doesn\'t make sense|nonsensical|gibberish)\b',
                    r'\b(what is this|what happened|where am i)\b'
                ],
                'medium': [
                    r'\b(confused|puzzled|bewildered|perplexed)\b',
                    r'\b(not sure|uncertain|unclear|vague)\b',
                    r'\b(how to|what do i|where do i)\b',
                    r'\b(explain|clarify|help me understand)\b',
                    r'\b(complicated|complex|difficult)\b'
                ],
                'low': [
                    r'\b(maybe|perhaps|possibly)\b',
                    r'\b(not clear|unclear|vague)\b',
                    r'\b(need help|assistance|guidance)\b'
                ]
            }
        }
        
        # Context indicators that can modify sentiment
        self.context_modifiers = {
            'negative_context': [
                r'\b(still|yet|again|once more)\b',
                r'\b(not working|broken|failed|error)\b',
                r'\b(same|identical|unchanged|no change)\b',
                r'\b(waiting|delayed|late|slow)\b',
                r'\b(expensive|costly|overpriced|high price)\b'
            ],
            'positive_context': [
                r'\b(now working|fixed|resolved|solved)\b',
                r'\b(improved|better|faster|easier)\b',
                r'\b(quick|fast|efficient|smooth)\b',
                r'\b(affordable|reasonable|good price)\b'
            ]
        }
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of chat/ticket text and return emotion category
        Uses Gemini AI when available, falls back to pattern matching
        """
        if not text or not text.strip():
            return 'neutral'
        
        # First try Gemini AI if available
        if GEMINI_AVAILABLE:
            try:
                print(f"🤖 Using Gemini AI for sentiment analysis")
                gemini_result = classify_emotion_with_gemini(text)
                
                # Map Gemini emotions to dashboard categories
                emotion_mapping = {
                    'angry': 'anger', 'frustrated': 'anger', 'furious': 'anger',
                    'irritated': 'anger', 'disgusted': 'anger', 'upset': 'anger',
                    'happy': 'joy', 'grateful': 'joy', 'thrilled': 'joy',
                    'delighted': 'joy', 'pleased': 'joy', 'satisfied': 'joy',
                    'confused': 'confusion', 'uncertain': 'confusion',
                    'puzzled': 'confusion', 'bewildered': 'confusion',
                    'neutral': 'neutral'
                }
                
                dashboard_emotion = emotion_mapping.get(gemini_result, 'neutral')
                print(f"🤖 Gemini result: '{gemini_result}' -> Dashboard: '{dashboard_emotion}'")
                return dashboard_emotion
                
            except Exception as e:
                print(f"❌ Gemini AI failed, falling back to pattern matching: {e}")
        
        # Fallback to pattern matching
        print(f"🔍 Using pattern matching fallback")
        text_lower = text.lower().strip()
        
        # Calculate emotion scores
        emotion_scores = self._calculate_emotion_scores(text_lower)
        
        # Apply context modifiers
        emotion_scores = self._apply_context_modifiers(text_lower, emotion_scores)
        
        # Determine dominant emotion
        dominant_emotion = self._get_dominant_emotion(emotion_scores)
        
        # Map to dashboard categories
        return self._map_to_dashboard_category(dominant_emotion)
    
    def _calculate_emotion_scores(self, text: str) -> Dict[str, float]:
        """Calculate emotion scores based on pattern matches"""
        scores = {'anger': 0.0, 'joy': 0.0, 'confusion': 0.0}
        
        for emotion, levels in self.emotion_patterns.items():
            for level, patterns in levels.items():
                weight = {'high': 3.0, 'medium': 2.0, 'low': 1.0}[level]
                for pattern in patterns:
                    matches = len(re.findall(pattern, text))
                    scores[emotion] += matches * weight
        
        return scores
    
    def _apply_context_modifiers(self, text: str, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply context-based modifications to emotion scores"""
        # Check for negative context that might increase anger
        negative_context = sum(len(re.findall(pattern, text)) for pattern in self.context_modifiers['negative_context'])
        if negative_context > 0:
            scores['anger'] += negative_context * 0.5
        
        # Check for positive context that might increase joy
        positive_context = sum(len(re.findall(pattern, text)) for pattern in self.context_modifiers['positive_context'])
        if positive_context > 0:
            scores['joy'] += positive_context * 0.5
        
        return scores
    
    def _get_dominant_emotion(self, scores: Dict[str, float]) -> str:
        """Determine the dominant emotion based on scores"""
        max_score = max(scores.values())
        
        # If no clear emotion, return neutral
        if max_score == 0:
            return 'neutral'
        
        # Find emotions with the highest score
        dominant_emotions = [emotion for emotion, score in scores.items() if score == max_score]
        
        # If multiple emotions tie, prefer anger over confusion, joy over neutral
        if len(dominant_emotions) > 1:
            if 'anger' in dominant_emotions:
                return 'anger'
            elif 'confusion' in dominant_emotions:
                return 'confusion'
            elif 'joy' in dominant_emotions:
                return 'joy'
        
        return dominant_emotions[0]
    
    def _map_to_dashboard_category(self, emotion: str) -> str:
        """Map internal emotion to dashboard category"""
        mapping = {
            'anger': 'anger',
            'joy': 'joy', 
            'confusion': 'confusion',
            'neutral': 'neutral'
        }
        return mapping.get(emotion, 'neutral')
    
    def get_sentiment_details(self, text: str) -> Dict[str, any]:
        """Get detailed sentiment analysis with scores and reasoning"""
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'reasoning': 'Empty or invalid text',
                'scores': {'anger': 0.0, 'joy': 0.0, 'confusion': 0.0}
            }
        
        # Try Gemini first if available
        if GEMINI_AVAILABLE:
            try:
                gemini_result = classify_emotion_with_gemini(text)
                emotion_mapping = {
                    'angry': 'anger', 'frustrated': 'anger', 'furious': 'anger',
                    'irritated': 'anger', 'disgusted': 'anger', 'upset': 'anger',
                    'happy': 'joy', 'grateful': 'joy', 'thrilled': 'joy',
                    'delighted': 'joy', 'pleased': 'joy', 'satisfied': 'joy',
                    'confused': 'confusion', 'uncertain': 'confusion',
                    'puzzled': 'confusion', 'bewildered': 'confusion',
                    'neutral': 'neutral'
                }
                
                dashboard_emotion = emotion_mapping.get(gemini_result, 'neutral')
                return {
                    'sentiment': dashboard_emotion,
                    'confidence': 0.9,  # High confidence for AI
                    'reasoning': f"Gemini AI classified as: {gemini_result}",
                    'method': 'gemini_ai',
                    'raw_result': gemini_result
                }
            except Exception as e:
                print(f"❌ Gemini AI failed in detailed analysis: {e}")
        
        # Fallback to pattern matching
        text_lower = text.lower().strip()
        emotion_scores = self._calculate_emotion_scores(text_lower)
        emotion_scores = self._apply_context_modifiers(text_lower, emotion_scores)
        
        dominant_emotion = self._get_dominant_emotion(emotion_scores)
        max_score = max(emotion_scores.values())
        total_score = sum(emotion_scores.values())
        
        confidence = (max_score / total_score) if total_score > 0 else 0.0
        
        # Generate reasoning
        reasoning_parts = []
        for emotion, score in emotion_scores.items():
            if score > 0:
                reasoning_parts.append(f"{emotion}: {score:.1f}")
        
        reasoning = f"Pattern matching detected {dominant_emotion} (confidence: {confidence:.2f}). Scores: {', '.join(reasoning_parts)}"
        
        return {
            'sentiment': self._map_to_dashboard_category(dominant_emotion),
            'confidence': round(confidence, 3),
            'reasoning': reasoning,
            'method': 'pattern_matching',
            'scores': {k: round(v, 2) for k, v in emotion_scores.items()}
        }

# Global instance
sentiment_analyzer = ChatTicketSentimentAnalyzer()

def analyze_chat_ticket_sentiment(text: str) -> str:
    """Simple function to get sentiment category for chat/ticket text"""
    return sentiment_analyzer.analyze_sentiment(text)

def get_detailed_sentiment(text: str) -> Dict[str, any]:
    """Get detailed sentiment analysis for debugging"""
    return sentiment_analyzer.get_sentiment_details(text) 