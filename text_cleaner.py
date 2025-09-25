import re
from typing import List, Tuple

class AIWatermarkRemover:
    """
    A class to identify and remove AI watermarks and disclaimers from text
    while preserving the original formatting.
    """
    
    def __init__(self):
        self.watermark_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """
        Compile regex patterns for identifying AI watermarks.
        Returns list of (compiled_pattern, description) tuples.
        """
        patterns = [
            # Common AI introductions
            (r'^As an AI\b.*?(?=\n\n|\n[A-Z]|$)', 'AI introduction'),
            (r'^I\'m an AI\b.*?(?=\n\n|\n[A-Z]|$)', 'AI self-identification'),
            (r'^I am an AI\b.*?(?=\n\n|\n[A-Z]|$)', 'AI self-identification'),
            (r'^As a language model\b.*?(?=\n\n|\n[A-Z]|$)', 'Language model disclaimer'),
            (r'^As an artificial intelligence\b.*?(?=\n\n|\n[A-Z]|$)', 'AI disclaimer'),
            
            # Disclaimers and limitations
            (r'^I don\'t have\b.*?(?=\n\n|\n[A-Z]|$)', 'Capability disclaimer'),
            (r'^I cannot\b.*?(?=\n\n|\n[A-Z]|$)', 'Capability disclaimer'),
            (r'^I\'m not able to\b.*?(?=\n\n|\n[A-Z]|$)', 'Capability disclaimer'),
            (r'^I don\'t have personal\b.*?(?=\n\n|\n[A-Z]|$)', 'Personal limitation'),
            (r'^I should mention that\b.*?(?=\n\n|\n[A-Z]|$)', 'Disclaimer introduction'),
            (r'^I should note that\b.*?(?=\n\n|\n[A-Z]|$)', 'Disclaimer introduction'),
            (r'^It\'s important to note\b.*?(?=\n\n|\n[A-Z]|$)', 'Important note disclaimer'),
            (r'^Please note that\b.*?(?=\n\n|\n[A-Z]|$)', 'Note disclaimer'),
            
            # Apologies and uncertainty
            (r'^I apologize,?\s+but\b.*?(?=\n\n|\n[A-Z]|$)', 'Apology disclaimer'),
            (r'^I\'m sorry,?\s+but\b.*?(?=\n\n|\n[A-Z]|$)', 'Apology disclaimer'),
            (r'^Sorry,?\s+but\b.*?(?=\n\n|\n[A-Z]|$)', 'Apology disclaimer'),
            
            # Responsibility and legal disclaimers
            (r'^Please consult\b.*?(?=\n\n|\n[A-Z]|$)', 'Consultation disclaimer'),
            (r'^You should consult\b.*?(?=\n\n|\n[A-Z]|$)', 'Consultation disclaimer'),
            (r'^This is not\b.*?advice.*?(?=\n\n|\n[A-Z]|$)', 'Not advice disclaimer'),
            (r'^Always consult\b.*?(?=\n\n|\n[A-Z]|$)', 'Consultation disclaimer'),
            
            # Mid-text disclaimers (more careful with these)
            (r'\s*\(As an AI[^)]*\)', 'Parenthetical AI disclaimer'),
            (r'\s*\[As an AI[^\]]*\]', 'Bracketed AI disclaimer'),
            (r'\s*--\s*As an AI\b.*?(?=\n|$)', 'Dashed AI disclaimer'),
            
            # Ending disclaimers
            (r'\n\n.*?(?:please consult|seek professional|not intended as).*?advice.*?$', 'Ending advice disclaimer'),
            (r'\n\n.*?(?:I\'m an AI|as an AI).*?$', 'Ending AI disclaimer'),
        ]
        
        compiled_patterns = []
        for pattern, description in patterns:
            try:
                compiled_patterns.append((re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL), description))
            except re.error as e:
                print(f"Warning: Could not compile pattern '{pattern}': {e}")
        
        return compiled_patterns
    
    def _preserve_formatting_markers(self, text: str) -> Tuple[str, dict]:
        """
        Extract and preserve formatting markers before cleaning.
        Returns (text_with_placeholders, formatting_map).
        """
        formatting_map = {}
        counter = 0
        
        # Preserve markdown formatting
        markdown_patterns = [
            (r'(\*\*.*?\*\*)', 'BOLD'),  # Bold
            (r'(\*.*?\*)', 'ITALIC'),     # Italic
            (r'(`.*?`)', 'CODE'),         # Inline code
            (r'(```.*?```)', 'CODEBLOCK'), # Code blocks
            (r'(#{1,6}\s+.*?(?=\n|$))', 'HEADER'), # Headers
            (r'(^\s*[-*+]\s+)', 'BULLET'), # Bullet points
            (r'(^\s*\d+\.\s+)', 'NUMBER'), # Numbered lists
        ]
        
        processed_text = text
        for pattern, marker_type in markdown_patterns:
            matches = re.finditer(pattern, processed_text, re.MULTILINE)
            for match in reversed(list(matches)):  # Reverse to maintain positions
                placeholder = f"__FORMAT_{counter}__"
                formatting_map[placeholder] = match.group(1)
                processed_text = processed_text[:match.start()] + placeholder + processed_text[match.end():]
                counter += 1
        
        return processed_text, formatting_map
    
    def _restore_formatting_markers(self, text: str, formatting_map: dict) -> str:
        """Restore formatting markers from the formatting map."""
        restored_text = text
        for placeholder, original in formatting_map.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text
    
    def clean_text(self, text: str) -> str:
        """
        Main method to clean AI watermarks from text while preserving formatting.
        
        Args:
            text: Input text that may contain AI watermarks
            
        Returns:
            Cleaned text with watermarks removed and formatting preserved
        """
        if not text or not text.strip():
            return text
        
        # Preserve formatting
        processed_text, formatting_map = self._preserve_formatting_markers(text)
        
        # Apply watermark removal patterns
        for pattern, description in self.watermark_patterns:
            processed_text = pattern.sub('', processed_text)
        
        # Clean up extra whitespace created by removals
        processed_text = self._clean_whitespace(processed_text)
        
        # Restore formatting
        cleaned_text = self._restore_formatting_markers(processed_text, formatting_map)
        
        return cleaned_text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean up excessive whitespace while preserving intentional formatting."""
        # Remove multiple consecutive blank lines (more than 2)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from lines
        text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
        
        # Remove leading/trailing whitespace from the entire text
        text = text.strip()
        
        return text
    
    def get_watermark_patterns(self) -> List[str]:
        """Return a list of watermark patterns being detected."""
        return [description for _, description in self.watermark_patterns]