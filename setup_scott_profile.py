#!/usr/bin/env python3
"""
Script to analyze Scott's writing style from scott.md and create a personalized style profile.
"""

from style_analyzer import WritingStyleAnalyzer
import os

def setup_scott_style_profile():
    """
    Read Scott's writing samples and create a style profile.
    """
    
    # Read the writing sample
    scott_file = 'scott.md'
    if not os.path.exists(scott_file):
        print(f"Error: {scott_file} not found!")
        return False
    
    with open(scott_file, 'r', encoding='utf-8') as f:
        writing_sample = f.read()
    
    print("📝 Analyzing Scott's writing style...")
    print(f"Sample length: {len(writing_sample):,} characters")
    
    # Initialize the analyzer
    analyzer = WritingStyleAnalyzer()
    
    # Analyze the writing sample
    style_profile = analyzer.analyze_writing_sample(writing_sample)
    
    # Save the profile
    profile_path = 'user_style_profile.json'
    analyzer.save_profile(profile_path)
    
    # Get and display style summary
    summary = analyzer.get_style_summary()
    
    print("\n🎯 Scott's Writing Style Profile:")
    print("=" * 50)
    
    print(f"Average Sentence Length: {summary['avg_sentence_length']} words")
    print(f"Vocabulary Complexity: {summary['vocab_complexity']} avg letters/word")
    print(f"Contractions Usage: {summary['contractions_rate']}%")
    
    print(f"\nTop Words Used:")
    for word, count in list(summary['top_words'].items())[:8]:
        print(f"  • {word}: {count} times")
    
    print(f"\nCommon Phrases:")
    for phrase, count in list(summary['top_phrases'].items())[:5]:
        print(f"  • '{phrase}': {count} times")
    
    print(f"\nFavorite Sentence Starters:")
    for starter, count in list(summary['common_starters'].items())[:5]:
        print(f"  • '{starter}': {count} times")
    
    if summary['personal_expressions']:
        print(f"\nPersonal Expressions:")
        for expr in summary['personal_expressions'][:5]:
            print(f"  • '{expr}'")
    
    print(f"\n✅ Style profile saved to: {profile_path}")
    print("\nNow you can use the 'Humanize to match my style' option in the web app!")
    
    return True

def demonstrate_humanization():
    """
    Show how Scott's style would transform some sample AI text.
    """
    from text_cleaner import AIWatermarkRemover
    from style_analyzer import TextHumanizer
    import json
    
    # Load Scott's style profile
    with open('user_style_profile.json', 'r') as f:
        style_profile = json.load(f)
    
    # Sample AI text to transform
    ai_text = """As an AI language model, I can provide information about the benefits of implementing artificial intelligence in business operations. 

It is important to note that artificial intelligence technologies can significantly enhance operational efficiency and productivity. Organizations should consider utilizing machine learning algorithms to optimize their data processing capabilities. Furthermore, it is recommended that businesses conduct thorough analysis before implementing AI solutions.

I should mention that proper planning and strategic implementation are essential for successful AI adoption. Please consult with technology experts to ensure optimal results, as this information is for general guidance purposes only."""
    
    print("\n" + "="*60)
    print("🧪 DEMONSTRATION: Scott's Style Transformation")
    print("="*60)
    
    print("\n📄 ORIGINAL AI TEXT:")
    print("-" * 30)
    print(ai_text)
    
    # Clean AI watermarks
    cleaner = AIWatermarkRemover()
    cleaned_text = cleaner.clean_text(ai_text)
    
    print("\n🧹 AFTER CLEANING (AI watermarks removed):")
    print("-" * 30)
    print(cleaned_text)
    
    # Humanize using Scott's style
    humanizer = TextHumanizer(style_profile)
    humanized_text = humanizer.humanize_text(cleaned_text)
    
    print("\n🎨 AFTER HUMANIZATION (Scott's style applied):")
    print("-" * 30)
    print(humanized_text)
    
    print("\n📊 TRANSFORMATION ANALYSIS:")
    print("-" * 30)
    print(f"Original length: {len(ai_text)} characters")
    print(f"Cleaned length: {len(cleaned_text)} characters")
    print(f"Humanized length: {len(humanized_text)} characters")
    
    reduction = ((len(ai_text) - len(cleaned_text)) / len(ai_text)) * 100
    print(f"AI watermark reduction: {reduction:.1f}%")
    
    style_change = ((len(cleaned_text) - len(humanized_text)) / len(cleaned_text)) * 100
    print(f"Style transformation: {style_change:.1f}% length change")

if __name__ == "__main__":
    print("🚀 Setting up Scott's Writing Style Profile")
    print("=" * 50)
    
    success = setup_scott_style_profile()
    
    if success:
        print("\n" + "="*50)
        print("Would you like to see a demonstration of how your")
        print("style transforms AI text? (y/n): ", end="")
        
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes']:
                demonstrate_humanization()
        except KeyboardInterrupt:
            print("\n\n👋 Setup complete! You can now use the web app.")
    
    print("\n🎯 Next Steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Check 'Humanize to match my style' when cleaning text")
    print("4. Enjoy AI text that sounds like Scott wrote it! 🎉")