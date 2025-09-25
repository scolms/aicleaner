import re
import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import statistics

class WritingStyleAnalyzer:
    """
    Analyzes writing samples to build a profile of the user's writing style.
    """
    
    def __init__(self):
        self.style_profile = {
            'sentence_lengths': [],
            'paragraph_lengths': [],
            'common_words': {},
            'common_phrases': {},
            'punctuation_patterns': {},
            'sentence_starters': {},
            'transition_words': {},
            'tone_indicators': {},
            'contractions_usage': 0.0,
            'passive_voice_usage': 0.0,
            'avg_sentence_length': 0.0,
            'vocabulary_complexity': 0.0,
            'personal_expressions': [],
        }
    
    def analyze_writing_sample(self, text: str) -> Dict:
        """
        Analyze a writing sample and extract style characteristics.
        """
        if not text.strip():
            return self.style_profile
        
        # Clean and prepare text
        cleaned_text = self._clean_text(text)
        sentences = self._extract_sentences(cleaned_text)
        paragraphs = self._extract_paragraphs(cleaned_text)
        
        # Analyze various aspects
        self._analyze_sentence_structure(sentences)
        self._analyze_vocabulary(sentences)
        self._analyze_tone_and_style(sentences)
        self._analyze_punctuation(text)
        self._analyze_paragraph_structure(paragraphs)
        
        return self.style_profile
    
    def _clean_text(self, text: str) -> str:
        """Clean text while preserving important punctuation."""
        # Remove excessive whitespace but preserve structure
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        # Simple sentence splitting (can be improved with NLTK)
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_paragraphs(self, text: str) -> List[str]:
        """Extract paragraphs from text."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _analyze_sentence_structure(self, sentences: List[str]):
        """Analyze sentence length and structure patterns."""
        lengths = [len(sentence.split()) for sentence in sentences]
        self.style_profile['sentence_lengths'].extend(lengths)
        
        if lengths:
            self.style_profile['avg_sentence_length'] = statistics.mean(lengths)
        
        # Analyze sentence starters
        starters = {}
        for sentence in sentences:
            words = sentence.split()
            if words:
                starter = words[0].lower()
                starters[starter] = starters.get(starter, 0) + 1
        
        self.style_profile['sentence_starters'].update(starters)
    
    def _analyze_vocabulary(self, sentences: List[str]):
        """Analyze vocabulary usage and complexity."""
        all_words = []
        word_counts = Counter()
        
        for sentence in sentences:
            words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
            all_words.extend(words)
            word_counts.update(words)
        
        # Update common words
        for word, count in word_counts.most_common(50):
            if word not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']:
                self.style_profile['common_words'][word] = self.style_profile['common_words'].get(word, 0) + count
        
        # Analyze vocabulary complexity (average word length)
        if all_words:
            avg_word_length = sum(len(word) for word in all_words) / len(all_words)
            self.style_profile['vocabulary_complexity'] = avg_word_length
        
        # Detect common phrases (2-3 word combinations)
        text_joined = ' '.join(sentences).lower()
        bigrams = re.findall(r'\b\w+\s+\w+\b', text_joined)
        trigrams = re.findall(r'\b\w+\s+\w+\s+\w+\b', text_joined)
        
        for phrase in bigrams + trigrams:
            if len(phrase.split()) >= 2:
                self.style_profile['common_phrases'][phrase] = self.style_profile['common_phrases'].get(phrase, 0) + 1
    
    def _analyze_tone_and_style(self, sentences: List[str]):
        """Analyze tone indicators and style markers."""
        text = ' '.join(sentences).lower()
        
        # Contraction usage
        contractions = len(re.findall(r"\b\w+'\w+\b", text))
        total_words = len(text.split())
        if total_words > 0:
            self.style_profile['contractions_usage'] = contractions / total_words
        
        # Passive voice detection (simple heuristic)
        passive_indicators = ['was', 'were', 'been', 'being', 'be']
        passive_count = sum(text.count(f' {indicator} ') for indicator in passive_indicators)
        if len(sentences) > 0:
            self.style_profile['passive_voice_usage'] = passive_count / len(sentences)
        
        # Transition words
        transitions = ['however', 'therefore', 'moreover', 'furthermore', 'nevertheless', 
                      'meanwhile', 'consequently', 'thus', 'hence', 'accordingly']
        
        for transition in transitions:
            count = text.count(transition)
            if count > 0:
                self.style_profile['transition_words'][transition] = count
        
        # Personal expressions and style markers
        personal_markers = [
            r"\bi think\b", r"\bi believe\b", r"\bin my opinion\b", r"\bi feel\b",
            r"\bto me\b", r"\bpersonally\b", r"\bobviously\b", r"\bclearly\b",
            r"\bbasically\b", r"\bactually\b", r"\bhonestly\b"
        ]
        
        for marker in personal_markers:
            matches = re.findall(marker, text)
            if matches:
                self.style_profile['personal_expressions'].extend(matches)
    
    def _analyze_punctuation(self, text: str):
        """Analyze punctuation usage patterns."""
        punctuation_counts = Counter()
        
        # Count different punctuation marks
        for char in text:
            if char in '.,;:!?-()[]{}"\'/':
                punctuation_counts[char] += 1
        
        # Calculate ratios
        total_chars = len(text)
        if total_chars > 0:
            for punct, count in punctuation_counts.items():
                self.style_profile['punctuation_patterns'][punct] = count / total_chars
    
    def _analyze_paragraph_structure(self, paragraphs: List[str]):
        """Analyze paragraph length and structure."""
        para_lengths = [len(paragraph.split()) for paragraph in paragraphs]
        self.style_profile['paragraph_lengths'].extend(para_lengths)
    
    def save_profile(self, filepath: str):
        """Save the writing style profile to a file."""
        with open(filepath, 'w') as f:
            json.dump(self.style_profile, f, indent=2)
    
    def load_profile(self, filepath: str):
        """Load a writing style profile from a file."""
        try:
            with open(filepath, 'r') as f:
                self.style_profile = json.load(f)
        except FileNotFoundError:
            print(f"Profile file {filepath} not found. Using default profile.")
    
    def get_style_summary(self) -> Dict:
        """Get a summary of the writing style profile."""
        return {
            'avg_sentence_length': round(self.style_profile['avg_sentence_length'], 1),
            'vocab_complexity': round(self.style_profile['vocabulary_complexity'], 1),
            'contractions_rate': round(self.style_profile['contractions_usage'] * 100, 1),
            'top_words': dict(Counter(self.style_profile['common_words']).most_common(10)),
            'top_phrases': dict(Counter(self.style_profile['common_phrases']).most_common(5)),
            'common_starters': dict(Counter(self.style_profile['sentence_starters']).most_common(5)),
            'personal_expressions': list(set(self.style_profile['personal_expressions']))[:10]
        }


class TextHumanizer:
    """
    Transforms AI-generated text to match a specific writing style profile.
    """
    
    def __init__(self, style_profile: Dict):
        self.style_profile = style_profile
    
    def humanize_text(self, text: str) -> str:
        """
        Transform text to match the writing style profile.
        """
        if not text.strip():
            return text
        
        # Apply various transformations
        humanized = text
        humanized = self._adjust_sentence_length(humanized)
        humanized = self._inject_personal_style(humanized)
        humanized = self._adjust_vocabulary(humanized)
        humanized = self._adjust_tone(humanized)
        
        return humanized
    
    def _adjust_sentence_length(self, text: str) -> str:
        """Adjust sentence lengths to match the user's style."""
        target_length = self.style_profile.get('avg_sentence_length', 15)
        
        sentences = re.split(r'[.!?]+', text)
        adjusted_sentences = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            words = sentence.strip().split()
            current_length = len(words)
            
            # If sentence is much longer than target, try to split
            if current_length > target_length * 1.5:
                # Find good split points (conjunctions, commas)
                split_points = []
                for i, word in enumerate(words):
                    if word.lower() in ['and', 'but', 'however', 'therefore', 'moreover']:
                        split_points.append(i)
                
                if split_points:
                    # Split at the middle-most conjunction
                    split_at = min(split_points, key=lambda x: abs(x - len(words)//2))
                    first_part = ' '.join(words[:split_at])
                    second_part = ' '.join(words[split_at:])
                    adjusted_sentences.extend([first_part.strip(), second_part.strip()])
                else:
                    adjusted_sentences.append(sentence.strip())
            else:
                adjusted_sentences.append(sentence.strip())
        
        return '. '.join(adjusted_sentences) + ('.' if adjusted_sentences else '')
    
    def _inject_personal_style(self, text: str) -> str:
        """Inject personal expressions and style markers."""
        # Add contractions if the user uses them frequently
        contraction_rate = self.style_profile.get('contractions_usage', 0)
        
        if contraction_rate > 0.1:  # If user uses contractions more than 10% of the time
            contractions_map = {
                'do not': "don't", 'does not': "doesn't", 'did not': "didn't",
                'will not': "won't", 'would not': "wouldn't", 'could not': "couldn't",
                'should not': "shouldn't", 'cannot': "can't", 'is not': "isn't",
                'are not': "aren't", 'was not': "wasn't", 'were not': "weren't",
                'have not': "haven't", 'has not': "hasn't", 'had not': "hadn't"
            }
            
            for formal, informal in contractions_map.items():
                text = re.sub(r'\b' + formal + r'\b', informal, text, flags=re.IGNORECASE)
        
        # Add personal expressions occasionally
        personal_expressions = self.style_profile.get('personal_expressions', [])
        if personal_expressions and len(text.split('.')) > 1:
            # Randomly insert a personal expression
            sentences = text.split('.')
            if len(sentences) > 1:
                # Add "I think" or similar to one sentence
                import random
                if random.random() < 0.3:  # 30% chance
                    idx = random.randint(0, len(sentences) - 2)
                    sentence = sentences[idx].strip()
                    if sentence and not any(expr in sentence.lower() for expr in ['i think', 'i believe', 'in my opinion']):
                        if random.choice(['think', 'believe']) == 'think':
                            sentences[idx] = f"I think {sentence.lower()}"
                        else:
                            sentences[idx] = f"In my opinion, {sentence.lower()}"
                text = '. '.join(sentences)
        
        return text
    
    def _adjust_vocabulary(self, text: str) -> str:
        """Adjust vocabulary to match user's complexity level."""
        target_complexity = self.style_profile.get('vocabulary_complexity', 5)
        user_words = self.style_profile.get('common_words', {})
        
        # Simple vocabulary substitutions based on complexity
        if target_complexity < 5:  # User prefers simpler words
            complex_to_simple = {
                'utilize': 'use', 'commence': 'start', 'terminate': 'end',
                'demonstrate': 'show', 'facilitate': 'help', 'implement': 'do',
                'acquire': 'get', 'substantial': 'big', 'eliminate': 'remove',
                'approximately': 'about', 'consequently': 'so', 'furthermore': 'also'
            }
            
            for complex_word, simple_word in complex_to_simple.items():
                text = re.sub(r'\b' + complex_word + r'\b', simple_word, text, flags=re.IGNORECASE)
        
        # Replace words with user's preferred alternatives
        if user_words:
            # This is a simplified approach - in practice, you'd want more sophisticated word mapping
            common_user_words = dict(Counter(user_words).most_common(20))
            for user_word in common_user_words:
                # Could implement synonym replacement here
                pass
        
        return text
    
    def _adjust_tone(self, text: str) -> str:
        """Adjust tone to match user's style."""
        # If user has low passive voice usage, convert some passive to active
        passive_usage = self.style_profile.get('passive_voice_usage', 0)
        
        if passive_usage < 0.1:  # User rarely uses passive voice
            # Simple passive to active conversion (basic approach)
            text = re.sub(r'\bis being\s+(\w+ed)\b', r'is \1ing', text)
            text = re.sub(r'\bwas\s+(\w+ed)\s+by\s+(\w+)', r'\2 \1', text)
        
        return text