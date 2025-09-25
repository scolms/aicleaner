"""
Test cases for the AI Text Cleaner
"""

test_cases = [
    {
        "name": "Basic AI Introduction",
        "input": """As an AI language model, I'd be happy to help you with your question about renewable energy.

Renewable energy sources offer many benefits including environmental protection and long-term cost savings.""",
        "expected_removal": ["As an AI language model, I'd be happy to help you with your question about renewable energy."]
    },
    
    {
        "name": "AI Self-Identification",
        "input": """I'm an AI assistant created by Anthropic. Here's what I think about the topic:

Machine learning is a fascinating field that has applications in many areas of technology.""",
        "expected_removal": ["I'm an AI assistant created by Anthropic."]
    },
    
    {
        "name": "Multiple Disclaimers",
        "input": """As an AI, I don't have personal experiences, but I can provide information.

The benefits of exercise include:
1. Improved cardiovascular health
2. Better mental wellbeing
3. Increased strength and flexibility

I should mention that you should consult with a healthcare professional before starting any new exercise routine.""",
        "expected_removal": ["As an AI, I don't have personal experiences, but I can provide information.", "I should mention that you should consult with a healthcare professional before starting any new exercise routine."]
    },
    
    {
        "name": "Formatted Text with AI Disclaimers",
        "input": """I'm an AI assistant, so I don't have personal opinions, but I can share some information.

# Benefits of Reading

Reading regularly has numerous advantages:

* **Improved vocabulary** - Exposure to new words
* **Better focus** - Concentration skills development
* **Stress reduction** - Mental relaxation

```python
def read_book():
    return "knowledge gained"
```

Please note that these are general benefits and individual experiences may vary.""",
        "expected_removal": ["I'm an AI assistant, so I don't have personal opinions, but I can share some information.", "Please note that these are general benefits and individual experiences may vary."]
    },
    
    {
        "name": "Medical Disclaimer",
        "input": """Here are some common symptoms of vitamin D deficiency:

- Fatigue and tiredness
- Bone pain and muscle weakness
- Depression or mood changes

This information is for educational purposes only and should not be considered medical advice. Always consult with a healthcare professional for proper diagnosis and treatment.""",
        "expected_removal": ["This information is for educational purposes only and should not be considered medical advice. Always consult with a healthcare professional for proper diagnosis and treatment."]
    },
    
    {
        "name": "Clean Text (No AI Watermarks)",
        "input": """The Industrial Revolution transformed society in the 18th and 19th centuries.

Key changes included:
1. Mass production in factories
2. Urbanization as people moved to cities
3. New transportation systems like railways

This period laid the foundation for modern industrial society.""",
        "expected_removal": []
    },
    
    {
        "name": "Apology Disclaimers",
        "input": """I apologize, but I cannot provide specific investment advice.

However, I can share some general principles of investing:

- Diversification reduces risk
- Time in the market beats timing the market
- Consider your risk tolerance

I'm sorry, but for personalized advice, you should consult with a financial advisor.""",
        "expected_removal": ["I apologize, but I cannot provide specific investment advice.", "I'm sorry, but for personalized advice, you should consult with a financial advisor."]
    }
]

def run_tests():
    """Run test cases against the AI cleaner"""
    from text_cleaner import AIWatermarkRemover
    
    cleaner = AIWatermarkRemover()
    results = []
    
    for test_case in test_cases:
        print(f"\n=== Testing: {test_case['name']} ===")
        print(f"Original length: {len(test_case['input'])} characters")
        
        cleaned = cleaner.clean_text(test_case['input'])
        
        print(f"Cleaned length: {len(cleaned)} characters")
        reduction = (len(test_case['input']) - len(cleaned)) / len(test_case['input']) * 100
        print(f"Reduction: {reduction:.1f}%")
        
        print(f"\nOriginal:")
        print(repr(test_case['input']))
        print(f"\nCleaned:")
        print(repr(cleaned))
        
        # Check if expected removals are gone
        removals_found = []
        for expected_removal in test_case['expected_removal']:
            if expected_removal.lower() in cleaned.lower():
                removals_found.append(expected_removal)
        
        success = len(removals_found) == 0
        
        results.append({
            'name': test_case['name'],
            'success': success,
            'reduction_percent': reduction,
            'missed_removals': removals_found
        })
        
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
        if not success:
            print(f"Missed removals: {removals_found}")
        
        print("-" * 50)
    
    # Summary
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\n=== SUMMARY ===")
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    return results

if __name__ == "__main__":
    run_tests()