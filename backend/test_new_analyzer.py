#!/usr/bin/env python3
# test_new_analyzer.py
# Test script for the new chat/ticket sentiment analyzer

from chat_ticket_sentiment_analyzer import analyze_chat_ticket_sentiment, get_detailed_sentiment

def test_sentiment_analyzer():
    """Test various text samples with the new sentiment analyzer"""
    
    test_cases = [
        # Angry/Frustrated cases
        ("the product is still the same, not working", "anger"),
        ("I'm so frustrated with this service", "anger"),
        ("This is terrible and I hate it", "anger"),
        ("The app keeps crashing, I'm fed up", "anger"),
        ("Why is this so complicated and slow?", "anger"),
        
        # Happy/Joy cases
        ("Thank you so much, this is amazing!", "joy"),
        ("The product works perfectly now", "joy"),
        ("I love how fast and easy this is", "joy"),
        ("Excellent service, very satisfied", "joy"),
        ("This is exactly what I needed, thank you", "joy"),
        
        # Confusion cases
        ("I'm confused about how to use this", "confusion"),
        ("Can you explain what this means?", "confusion"),
        ("I don't understand the instructions", "confusion"),
        ("This is unclear and I need help", "confusion"),
        ("What am I supposed to do next?", "confusion"),
        
        # Neutral cases
        ("Just checking the status", "neutral"),
        ("I have a question about billing", "neutral"),
        ("Can you send me the invoice?", "neutral"),
        ("What are your business hours?", "neutral"),
        ("I need to update my information", "neutral")
    ]
    
    print("🧪 Testing New Sentiment Analyzer\n")
    print("=" * 60)
    
    correct = 0
    total = len(test_cases)
    
    for text, expected in test_cases:
        result = analyze_chat_ticket_sentiment(text)
        detailed = get_detailed_sentiment(text)
        
        status = "✅" if result == expected else "❌"
        print(f"{status} Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        print(f"   Expected: {expected}, Got: {result}")
        print(f"   Confidence: {detailed['confidence']}")
        print(f"   Reasoning: {detailed['reasoning']}")
        print()
        
        if result == expected:
            correct += 1
    
    print("=" * 60)
    print(f"🎯 Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
    
    if correct == total:
        print("🎉 All tests passed! The analyzer is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the patterns and weights.")

if __name__ == "__main__":
    test_sentiment_analyzer() 