from flask import Flask, render_template, request, jsonify
from text_cleaner import AIWatermarkRemover
from style_analyzer import WritingStyleAnalyzer, TextHumanizer
from text_formatter import TextFormatter
import os
import json
import uuid

# Optional: Ollama integration (local LLM). We handle missing package gracefully.
try:
    import ollama  # type: ignore
except Exception:  # ImportError or runtime errors when daemon isn't available
    ollama = None  # Fallback below will handle this

app = Flask(__name__)
app.config['SECRET_KEY'] = 'scottify-ai-text-humanizer-2025'

cleaner = AIWatermarkRemover()
style_analyzer = WritingStyleAnalyzer()
formatter = TextFormatter()

# Load existing style profile if available
STYLE_PROFILE_PATH = 'user_style_profile.json'
if os.path.exists(STYLE_PROFILE_PATH):
    style_analyzer.load_profile(STYLE_PROFILE_PATH)

# Persona storage (simple JSON file). Each persona: {id, name, description, voice, tone, rules}
PERSONAS_PATH = 'personas.json'

def load_personas():
    try:
        if os.path.exists(PERSONAS_PATH):
            with open(PERSONAS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {"personas": [], "active_id": None}

def save_personas(data):
    with open(PERSONAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_active_persona():
    data = load_personas()
    active_id = data.get('active_id')
    if not active_id:
        return None
    for p in data.get('personas', []):
        if p.get('id') == active_id:
            return p
    return None


def _style_prompt(style_summary: dict, for_generation: bool = False) -> str:
    """Build a concise style brief for the LLM from the user's profile."""
    if not style_summary:
        return (
            "Voice: clear, friendly, confident.\n"
            "Tone: conversational, direct, avoid fluff.\n"
            "Pacing: varied sentence lengths, mostly short to medium.\n"
            "Contractions: use when natural.\n"
        )

    avg_len = style_summary.get('avg_sentence_length')
    vocab = style_summary.get('vocab_complexity')
    contr = style_summary.get('contractions_rate')
    
    if for_generation:
        # For content generation, focus only on structural patterns, not content words
        return (
            f"Target sentence length: ~{avg_len} words.\n"
            f"Vocabulary complexity (avg letters/word): ~{vocab}.\n"
            f"Contractions usage: ~{contr}%. Use contractions accordingly.\n"
            "Voice: authentic, human, specific. Avoid generic AI phrases.\n"
            "Tone: confident, helpful; remove hedging and corporate filler.\n"
            "Focus on writing RHYTHM and FLOW patterns, not specific vocabulary.\n"
        )
    else:
        # For text transformation, we can include more specific style elements
        starters = ", ".join((style_summary.get('common_starters') or {}).keys())
        top_words = ", ".join((style_summary.get('top_words') or {}).keys())
        personal = ", ".join(style_summary.get('personal_expressions') or [])

        return (
            f"Target sentence length: ~{avg_len} words.\n"
            f"Vocabulary complexity (avg letters/word): ~{vocab}.\n"
            f"Contractions usage: ~{contr}%. Use contractions accordingly.\n"
            f"Common starters: {starters if starters else 'n/a'}.\n"
            f"Preferred words: {top_words if top_words else 'n/a'}.\n"
            f"Personal expressions to sprinkle sparingly: {personal if personal else 'n/a'}.\n"
            "Voice: authentic, human, specific. Avoid generic AI phrases (e.g., 'as an AI').\n"
            "Tone: confident, helpful; remove hedging and corporate filler.\n"
        )

def _persona_prompt(persona: dict | None) -> str:
    if not persona:
        return ""
    parts = [
        f"Persona: {persona.get('name','')}",
        persona.get('description',''),
    ]
    voice = persona.get('voice')
    tone = persona.get('tone')
    rules = persona.get('rules')
    if voice:
        parts.append(f"Voice guidelines: {voice}")
    if tone:
        parts.append(f"Tone guidelines: {tone}")
    if rules:
        parts.append(f"Specific rules: {rules}")
    return "\n".join([p for p in parts if p]) + "\n"


def _format_instructions(fmt: str) -> str:
    """Give the LLM formatting focus while we still post-format with our formatter."""
    fmt = (fmt or 'standard').lower()
    if fmt == 'linkedin':
        return (
            "Format intent: LinkedIn post. Structure:\n"
            "- Start with an engaging hook (1-2 sentences)\n"
            "- Use short paragraphs (1-3 lines each)\n"
            "- Include bullets or numbered points when explaining concepts\n"
            "- Add 1-2 relevant emojis sparingly\n"
            "- End with a question or call-to-action to drive engagement\n"
            "- Keep it conversational and accessible, not academic\n"
            "- Total length: 200-400 words max\n"
            "- No markdown syntax—plain text only.\n"
        )
    if fmt == 'word':
        return (
            "Format intent: Business document. Clear headings inline, full sentences,\n"
            "formal but approachable tone. No markdown—plain text only.\n"
        )
    if fmt == 'notes':
        return (
            "Format intent: Concise notes. Bulleted lists, short lines, action items.\n"
            "No markdown—plain text bullets only.\n"
        )
    return (
        "Format intent: Standard article. Clear flow, short paragraphs, readable cadence.\n"
        "No markdown—plain text only.\n"
    )


def _token_similarity(a: str, b: str) -> float:
    """Rough Jaccard similarity over lowercased word sets to detect near-copies."""
    A = set(w for w in a.lower().split())
    B = set(w for w in b.lower().split())
    if not A or not B:
        return 0.0
    inter = len(A & B)
    union = len(A | B)
    return inter / union if union else 0.0


def generate_content_with_ollama(prompt: str, style_summary: dict, output_format: str, persona: dict | None) -> str:
    """Generate new content using Ollama model based on user prompt and style/persona."""
    if not ollama:
        raise RuntimeError("Ollama Python package or daemon not available")

    model = os.getenv('SCOTTIFY_OLLAMA_MODEL', 'gemma3:12b')
    
    # Build persona-specific instructions
    persona_emphasis = ""
    if persona:
        persona_name = persona.get('name', 'Active Persona')
        persona_voice = persona.get('voice', '')
        persona_tone = persona.get('tone', '')
        persona_rules = persona.get('rules', '')
        
        persona_emphasis = (
            f"PERSONA REQUIREMENTS - You must write as '{persona_name}':\n"
            f"Voice: {persona_voice}\n"
            f"Tone: {persona_tone}\n"
            f"Rules: {persona_rules}\n"
            "Make sure the content clearly reflects this persona's voice, tone, and style rules.\n\n"
        )
    
    system_prompt = (
        "You are Scottify, a content creator that generates completely original content in an authentic human voice.\n"
        "Create engaging, fresh content based ONLY on the user's request topic.\n\n"
        f"{persona_emphasis}"
        "Write using the STRUCTURAL PATTERNS and VOICE from the style guide, but DO NOT copy any specific phrases, metaphors, or subject matter from the style examples.\n"
        "Focus on:\n"
        "- Sentence rhythm and flow patterns\n"
        "- Vocabulary complexity level\n"
        "- Paragraph structure and pacing\n"
        "- Voice tone and personality (especially from persona)\n"
        "- Writing cadence and punctuation style\n\n"
        "CRITICALLY IMPORTANT: Generate completely original content about the requested topic. Do not reference or include any specific concepts, metaphors, or subject matter from the writing samples.\n"
        "The samples are only for learning writing STYLE and STRUCTURE, not content.\n\n"
        "Do not add prefaces, explanations, or meta-commentary. Return only the requested content as plain text.\n"
        "Avoid generic AI phrases, disclaimers, and corporate filler.\n\n"
        f"Style Structure Guide (for rhythm/flow only):\n{_style_prompt(style_summary, for_generation=True)}\n\n"
        f"Persona Voice Guidelines:\n{_persona_prompt(persona)}\n"
        f"Formatting Intent:\n{_format_instructions(output_format)}\n"
    )

    persona_reminder = ""
    if persona:
        persona_reminder = f"\n\nIMPORTANT: Write this in the voice and tone of '{persona.get('name', 'the specified persona')}'. Follow their voice guidelines: {persona.get('voice', 'N/A')}. Use their tone: {persona.get('tone', 'N/A')}. Apply their rules: {persona.get('rules', 'N/A')}."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Write completely original content about: {prompt}\n\nRemember: Use ONLY the sentence structure, rhythm, and voice patterns from the style guide. Do NOT include any specific words, phrases, concepts, or subject matter from the writing samples. Create fresh, original content about the requested topic.{persona_reminder}"},
    ]

    try:
        resp = ollama.chat(model=model, messages=messages, options={
            "temperature": 0.8,
            "top_p": 0.9,
            "num_ctx": 4096,
            "repeat_penalty": 1.1
        })
        content = resp.get('message', {}).get('content', '').strip()
        
        # If content seems too formal or academic for the persona, try once more with stronger emphasis
        if persona and content and _is_too_formal_for_persona(content, persona):
            retry_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": (
                    f"The previous attempt was too formal/academic. Write about: {prompt}\n\n"
                    f"CRITICAL: Write in a much more casual, conversational tone matching '{persona.get('name')}' persona. "
                    f"Use their voice: {persona.get('voice', '')}. "
                    f"Match their tone: {persona.get('tone', '')}. "
                    f"Follow their rules: {persona.get('rules', '')}. "
                    "Make it sound like a real person talking, not an academic paper."
                )}
            ]
            try:
                resp2 = ollama.chat(model=model, messages=retry_messages, options={
                    "temperature": 0.9,
                    "top_p": 0.95,
                    "num_ctx": 4096,
                    "repeat_penalty": 1.15
                })
                content2 = resp2.get('message', {}).get('content', '').strip()
                if content2:
                    content = content2
            except Exception:
                pass  # Use original content if retry fails
        
        return content or "Sorry, I couldn't generate content for that request."
    except Exception as e:
        raise RuntimeError(f"Ollama content generation failed: {e}")


def _is_too_formal_for_persona(content: str, persona: dict) -> bool:
    """Quick check if content seems too formal/academic for a casual persona."""
    if not persona:
        return False
    
    # Check persona tone for casual indicators
    tone = (persona.get('tone', '') + ' ' + persona.get('voice', '')).lower()
    is_casual_persona = any(word in tone for word in ['casual', 'friendly', 'humorous', 'plain', 'conversational'])
    
    if not is_casual_persona:
        return False
    
    # Check for formal/academic language patterns
    formal_indicators = [
        'constitutes', 'encompasses', 'illuminates', 'embodies', 'facilitates',
        'establishes', 'furthermore', 'moreover', 'consequently', 'thus',
        'represents a', 'provides the', 'requires a', 'demonstrates',
        'nuanced understanding', 'interwoven disciplines', 'aspiration',
        'cognitive functions', 'methodologies'
    ]
    
    content_lower = content.lower()
    formal_count = sum(1 for phrase in formal_indicators if phrase in content_lower)
    
    # If more than 2 formal indicators in casual persona content, it's likely too formal
    return formal_count > 2


def generate_with_ollama(cleaned_text: str, style_summary: dict, output_format: str, persona: dict | None) -> str:
    """Use a local Ollama model (gemma3:12b) to humanize text to the user's voice."""
    if not ollama:
        raise RuntimeError("Ollama Python package or daemon not available")

    model = os.getenv('SCOTTIFY_OLLAMA_MODEL', 'gemma3:12b')
    system_prompt = (
        "You are Scottify, a writing coach that rewrites content into an authentic human voice.\n"
        "Preserve the meaning; remove generic AI phrasing, disclaimers, and filler.\n"
        "Do not add prefaces or explanations. Return only the rewritten content as plain text.\n"
        "Important: Do not copy sentences or structure verbatim. Substantially rephrase to fit the persona and style,\n"
        "vary sentence length and cadence, and aim for noticeable lexical change (roughly 40–60%) while preserving intent.\n\n"
        f"Style Brief:\n{_style_prompt(style_summary, for_generation=False)}\n\n"
        f"Persona Additions:\n{_persona_prompt(persona)}\n"
        f"Formatting Intent:\n{_format_instructions(output_format)}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Rewrite the following to match the style.\n\nINPUT:\n{cleaned_text}"},
    ]

    try:
        # First attempt
        resp = ollama.chat(model=model, messages=messages, options={
            "temperature": 0.8,
            "top_p": 0.9,
            "num_ctx": 4096,
            "repeat_penalty": 1.1
        })
        content = resp.get('message', {}).get('content', '').strip()
        if not content:
            return cleaned_text
        # If too similar, one retry with stronger instruction and higher temperature
        if _token_similarity(cleaned_text, content) > 0.9:
            retry_messages = [
                messages[0],
                {"role": "user", "content": (
                    "Rewrite much more boldly. Do not repeat the original phrasing; keep meaning but heavily rework structure, cadence, and word choice.\n\n"
                    f"INPUT:\n{cleaned_text}"
                )}
            ]
            resp2 = ollama.chat(model=model, messages=retry_messages, options={
                "temperature": 0.95,
                "top_p": 0.95,
                "num_ctx": 4096,
                "repeat_penalty": 1.15
            })
            content2 = resp2.get('message', {}).get('content', '').strip()
            if content2:
                content = content2
        return content or cleaned_text
    except Exception as e:
        # Bubble up to allow fallback
        raise RuntimeError(f"Ollama chat failed: {e}")

@app.route('/')
def index():
    return render_template('index.html')

def is_generation_command(text: str) -> tuple[bool, str]:
    """Check if text starts with generation command and extract prompt."""
    text = text.strip()
    generation_prefixes = ['@gen ', '@generate ', '@Gen ', '@Generate ']
    
    for prefix in generation_prefixes:
        if text.lower().startswith(prefix.lower()):
            prompt = text[len(prefix):].strip()
            return True, prompt
    
    return False, ""


@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        output_format = data.get('format', 'standard')
        persona_id = data.get('persona_id')
        
        if not prompt.strip():
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Get style and persona
        style_summary = style_analyzer.get_style_summary()
        persona = None
        if persona_id:
            pdata = load_personas()
            persona = next((p for p in pdata.get('personas', []) if p.get('id') == persona_id), None)
        else:
            persona = get_active_persona()
        
        # Generate content
        try:
            generated_text = generate_content_with_ollama(prompt, style_summary, output_format, persona)
            engine_used = 'ollama'
        except Exception as e:
            return jsonify({
                'error': f'Content generation failed: {str(e)}',
                'fallback_message': 'Ollama is not available for content generation. Please ensure Ollama is installed and running.'
            }), 500
        
        # Format the output
        formatted_text = formatter.format_text(generated_text, output_format)
        
        return jsonify({
            'prompt': prompt,
            'generated': generated_text,
            'formatted': formatted_text,
            'format': output_format,
            'success': True,
            'generation_engine': engine_used,
            'persona_used': (persona or {}).get('id'),
            'persona_name': (persona or {}).get('name')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/scottify', methods=['POST'])
def scottify_text():
    try:
        data = request.get_json()
        input_text = data.get('text', '')
        humanize = data.get('humanize', False)
        output_format = data.get('format', 'standard')  # linkedin, word, notes, standard
        persona_id = data.get('persona_id')
        
        if not input_text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        # Check if this is a generation command
        is_gen_cmd, gen_prompt = is_generation_command(input_text)
        if is_gen_cmd:
            # Handle as content generation instead of text transformation
            try:
                style_summary = style_analyzer.get_style_summary()
                persona = None
                if persona_id:
                    pdata = load_personas()
                    persona = next((p for p in pdata.get('personas', []) if p.get('id') == persona_id), None)
                else:
                    persona = get_active_persona()
                
                generated_text = generate_content_with_ollama(gen_prompt, style_summary, output_format, persona)
                formatted_text = formatter.format_text(generated_text, output_format)
                
                return jsonify({
                    'original': input_text,
                    'prompt': gen_prompt,
                    'generated': generated_text,
                    'formatted': formatted_text,
                    'format': output_format,
                    'success': True,
                    'is_generation': True,
                    'generation_engine': 'ollama',
                    'persona_used': (persona or {}).get('id'),
                    'persona_name': (persona or {}).get('name'),
                    'style_summary': style_summary
                })
            except Exception as e:
                return jsonify({
                    'error': f'Content generation failed: {str(e)}',
                    'is_generation': True,
                    'fallback_message': 'Ollama is not available for content generation. Please ensure Ollama is installed and running.'
                }), 500
        
        # First, clean AI watermarks
        cleaned_text = cleaner.clean_text(input_text)
        
        # Then humanize if requested. Prefer Ollama if available; fallback to local humanizer.
        final_text = cleaned_text
        engine_used = 'local'
        persona_obj = None
        if humanize:
            style_summary = style_analyzer.get_style_summary()
            # Resolve persona (optional)
            persona = None
            if persona_id:
                pdata = load_personas()
                persona = next((p for p in pdata.get('personas', []) if p.get('id') == persona_id), None)
            else:
                persona = get_active_persona()
            persona_obj = persona
            try:
                final_text = generate_with_ollama(cleaned_text, style_summary, output_format, persona)
                engine_used = 'ollama'
            except Exception:
                # Fallback to heuristic humanizer if Ollama isn't available
                if style_analyzer.style_profile.get('avg_sentence_length', 0) > 0:
                    humanizer = TextHumanizer(style_analyzer.style_profile)
                    final_text = humanizer.humanize_text(cleaned_text)
        
        # Format the output according to selected style
        formatted_text = formatter.format_text(final_text, output_format)
        
        # Always get style summary for display
        style_summary_for_display = style_analyzer.get_style_summary()
        
        return jsonify({
            'original': input_text,
            'cleaned': cleaned_text,
            'humanized': final_text,
            'formatted': formatted_text,
            'format': output_format,
            'success': True,
            'humanization_applied': humanize,
            'humanization_engine': engine_used if humanize else 'none',
            'persona_used': (persona_obj or {}).get('id') if humanize else None,
            'persona_name': (persona_obj or {}).get('name') if humanize else None,
            'style_summary': style_summary_for_display
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Personas API
@app.route('/personas', methods=['GET'])
def list_personas():
    data = load_personas()
    return jsonify({
        'success': True,
        'personas': data.get('personas', []),
        'active_id': data.get('active_id')
    })


@app.route('/personas', methods=['POST'])
def create_persona():
    payload = request.get_json() or {}
    name = (payload.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Persona name is required'}), 400
    data = load_personas()
    pid = str(uuid.uuid4())
    persona = {
        'id': pid,
        'name': name,
        'description': (payload.get('description') or '').strip(),
        'voice': (payload.get('voice') or '').strip(),
        'tone': (payload.get('tone') or '').strip(),
        'rules': (payload.get('rules') or '').strip()
    }
    data.setdefault('personas', []).append(persona)
    # If no active persona, set this as active
    if not data.get('active_id'):
        data['active_id'] = pid
    save_personas(data)
    return jsonify({'success': True, 'persona': persona, 'active_id': data.get('active_id')})


@app.route('/personas/<pid>', methods=['PUT'])
def update_persona(pid):
    payload = request.get_json() or {}
    data = load_personas()
    updated = None
    for p in data.get('personas', []):
        if p.get('id') == pid:
            for key in ['name', 'description', 'voice', 'tone', 'rules']:
                if key in payload:
                    val = payload.get(key)
                    p[key] = (val.strip() if isinstance(val, str) else (val or ''))
            updated = p
            break
    if not updated:
        return jsonify({'error': 'Persona not found'}), 404
    save_personas(data)
    return jsonify({'success': True, 'persona': updated, 'active_id': data.get('active_id')})


@app.route('/personas/<pid>', methods=['DELETE'])
def delete_persona(pid):
    data = load_personas()
    personas = data.get('personas', [])
    new_list = [p for p in personas if p.get('id') != pid]
    if len(new_list) == len(personas):
        return jsonify({'error': 'Persona not found'}), 404
    data['personas'] = new_list
    if data.get('active_id') == pid:
        data['active_id'] = new_list[0]['id'] if new_list else None
    save_personas(data)
    return jsonify({'success': True, 'active_id': data.get('active_id')})


@app.route('/personas/activate', methods=['POST'])
def activate_persona():
    payload = request.get_json() or {}
    pid = payload.get('id')
    data = load_personas()
    if not any(p.get('id') == pid for p in data.get('personas', [])):
        return jsonify({'error': 'Persona not found'}), 404
    data['active_id'] = pid
    save_personas(data)
    return jsonify({'success': True, 'active_id': pid})

@app.route('/analyze-style', methods=['POST'])
def analyze_style():
    try:
        data = request.get_json()
        writing_sample = data.get('text', '')
        
        if not writing_sample.strip():
            return jsonify({'error': 'No writing sample provided'}), 400
        
        # Analyze the writing sample
        style_analyzer.analyze_writing_sample(writing_sample)
        
        # Save the updated profile
        style_analyzer.save_profile(STYLE_PROFILE_PATH)
        
        # Get style summary
        summary = style_analyzer.get_style_summary()
        
        return jsonify({
            'success': True,
            'style_summary': summary,
            'message': 'Writing style profile updated successfully!'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-style-profile', methods=['GET'])
def get_style_profile():
    try:
        summary = style_analyzer.get_style_summary()
        has_profile = style_analyzer.style_profile.get('avg_sentence_length', 0) > 0
        
        return jsonify({
            'success': True,
            'has_profile': has_profile,
            'style_summary': summary if has_profile else None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)