import re
from datetime import datetime
from typing import Dict, List

class TextFormatter:
    """
    Formats text output according to different styles: LinkedIn article, Word document, or notes.
    """
    
    def __init__(self):
        self.format_styles = {
            'linkedin': self._format_linkedin_article,
            'word': self._format_word_document,
            'notes': self._format_notes_style,
            'standard': self._format_standard
        }
    
    def format_text(self, text: str, format_style: str = 'standard') -> str:
        """
        Format text according to the specified style.
        
        Args:
            text: The input text to format
            format_style: The formatting style ('linkedin', 'word', 'notes', 'standard')
            
        Returns:
            Formatted text
        """
        if not text.strip():
            return text
        
        formatter = self.format_styles.get(format_style, self._format_standard)
        return formatter(text)
    
    def _format_linkedin_article(self, text: str) -> str:
        """
        Format text as a LinkedIn article with engaging structure.
        """
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return text
        
        formatted_parts = []
        
        # Add hook/opening if first paragraph is long enough
        if len(paragraphs[0].split()) > 15:
            # Create an engaging hook from the first sentence
            first_sentence = paragraphs[0].split('.')[0] + '.'
            hook = f"🚀 {first_sentence}\n\nHere's why this matters:"
            formatted_parts.append(hook)
            
            # Use rest of first paragraph
            remaining = paragraphs[0][len(first_sentence):].strip()
            if remaining:
                formatted_parts.append(remaining)
            
            paragraphs = paragraphs[1:]
        else:
            # Add emoji hook to first paragraph
            formatted_parts.append(f"💡 {paragraphs[0]}")
            paragraphs = paragraphs[1:]
        
        # Process remaining paragraphs
        for i, paragraph in enumerate(paragraphs):
            # Add section breaks and emphasis
            if len(paragraph.split()) > 20:  # Long paragraph
                # Split into smaller chunks
                sentences = paragraph.split('.')
                if len(sentences) > 2:
                    # Create subheadings for major points
                    formatted_parts.append(f"\n📍 Key Point {i+1}:")
                    formatted_parts.append('.'.join(sentences[:2]) + '.')
                    
                    if len(sentences) > 3:
                        formatted_parts.append('.'.join(sentences[2:]))
                else:
                    formatted_parts.append(paragraph)
            else:
                # Short paragraph - add emphasis
                if any(word in paragraph.lower() for word in ['important', 'key', 'critical', 'essential']):
                    formatted_parts.append(f"⚡ {paragraph}")
                else:
                    formatted_parts.append(paragraph)
        
        # Add call to action ending
        formatted_parts.append("\n---")
        formatted_parts.append("💭 What are your thoughts on this? Share your experience in the comments!")
        formatted_parts.append("\n#AI #Innovation #TechInsights #DigitalTransformation")
        
        return '\n\n'.join(formatted_parts)
    
    def _format_word_document(self, text: str) -> str:
        """
        Format text as a professional Word document with proper structure.
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return text
        
        formatted_parts = []
        
        # Add document header
        today = datetime.now().strftime("%B %d, %Y")
        formatted_parts.append(f"Document Created: {today}")
        formatted_parts.append("Author: Scott Colebourn")
        formatted_parts.append("=" * 50)
        
        # Add executive summary if content is substantial
        if len(paragraphs) > 2:
            # Create summary from first paragraph
            summary = paragraphs[0]
            if len(summary.split()) > 30:
                summary = '. '.join(summary.split('.')[:2]) + '.'
            
            formatted_parts.append("\nEXECUTIVE SUMMARY")
            formatted_parts.append("-" * 20)
            formatted_parts.append(summary)
            formatted_parts.append("")
        
        # Add main content with proper headings
        formatted_parts.append("MAIN CONTENT")
        formatted_parts.append("-" * 20)
        
        for i, paragraph in enumerate(paragraphs):
            # Add section numbers for longer content
            if len(paragraphs) > 3 and len(paragraph.split()) > 15:
                formatted_parts.append(f"\n{i+1}. Section {i+1}")
                formatted_parts.append(paragraph)
            else:
                formatted_parts.append(paragraph)
        
        # Add conclusion if multiple paragraphs
        if len(paragraphs) > 2:
            formatted_parts.append("\nCONCLUSION")
            formatted_parts.append("-" * 20)
            last_paragraph = paragraphs[-1]
            if len(last_paragraph.split()) > 10:
                formatted_parts.append(last_paragraph)
            else:
                formatted_parts.append("The key insights outlined above demonstrate the importance of strategic implementation and thoughtful consideration of the discussed concepts.")
        
        # Add footer
        formatted_parts.append("\n" + "=" * 50)
        formatted_parts.append(f"Generated via Scottify AI Text Processor | {today}")
        
        return '\n\n'.join(formatted_parts)
    
    def _format_notes_style(self, text: str) -> str:
        """
        Format text as quick, scannable notes with bullet points and highlights.
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return text
        
        formatted_parts = []
        
        # Add note header
        today = datetime.now().strftime("%m/%d/%y")
        formatted_parts.append(f"📝 Notes - {today}")
        formatted_parts.append("")
        
        for paragraph in paragraphs:
            # Convert paragraph to bullet points
            sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
            
            if len(sentences) == 1:
                # Single sentence - make it a main point
                formatted_parts.append(f"🔸 {sentences[0]}")
            elif len(sentences) <= 3:
                # Few sentences - keep together with emphasis
                formatted_parts.append(f"💡 {paragraph}")
            else:
                # Multiple sentences - break into bullets
                main_point = sentences[0]
                formatted_parts.append(f"🔹 {main_point}")
                
                for sentence in sentences[1:]:
                    if sentence:
                        formatted_parts.append(f"  • {sentence}")
                
                formatted_parts.append("")  # Add space after bullet group
        
        # Add quick action items if content suggests them
        action_keywords = ['should', 'need to', 'must', 'important to', 'consider', 'implement']
        action_items = []
        
        for paragraph in paragraphs:
            for keyword in action_keywords:
                if keyword in paragraph.lower():
                    # Extract action-oriented sentences
                    sentences = paragraph.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.split()) < 20:
                            action_items.append(sentence.strip())
                            break
        
        if action_items:
            formatted_parts.append("🎯 Action Items:")
            for item in action_items[:3]:  # Limit to top 3
                formatted_parts.append(f"  ☐ {item}")
        
        # Add tags
        formatted_parts.append("")
        formatted_parts.append("🏷️ Tags: #ai #notes #scottify #insights")
        
        return '\n'.join(formatted_parts)
    
    def _format_standard(self, text: str) -> str:
        """
        Standard formatting - clean paragraphs with proper spacing.
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Just clean up spacing and ensure proper paragraph breaks
        return '\n\n'.join(paragraphs)
    
    def get_available_formats(self) -> Dict[str, str]:
        """
        Return available formatting options with descriptions.
        """
        return {
            'standard': 'Clean, professional formatting',
            'linkedin': 'Engaging LinkedIn article with emojis and hashtags',
            'word': 'Formal document with headers and structure',
            'notes': 'Quick, scannable bullet-point notes'
        }