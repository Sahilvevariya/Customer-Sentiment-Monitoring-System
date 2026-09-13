#!/usr/bin/env python3
# test_gemini_classifier.py - Test Gemini emotion classifier

from gemini_emotion_classifier import classify_emotion_with_gemini

def test_gemini_classifier():
    test_text = "i am happy with the product"
    
    print(f"🧪 Testing Gemini classifier with: '{test_text}'")
    print("=" * 60)
    
    try:
        result = classify_emotion_with_gemini(test_text)
        print(f"\n🎯 Final result: {result}")
        
        if result == 'happy':
            print("✅ SUCCESS: Correctly classified as 'happy'")
        else:
            print(f"❌ FAILURE: Expected 'happy', got '{result}'")
            
    except Exception as e:
        print(f"❌ Error during classification: {e}")
    
    print("\n" + "=" * 60)
    
    # Test with other variations
    test_cases = [
        "I am happy with the product",
        "This product makes me very happy",
        "I love this product, it's amazing",
        "Thank you for this wonderful product"
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: '{test_case}'")
        try:
            result = classify_emotion_with_gemini(test_case)
            print(f"🎯 Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gemini_classifier()
