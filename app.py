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


def _style_prompt(style_summary: dict) -> str:
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
            "Format intent: LinkedIn post. Use a bold hook, short paragraphs (1-3 lines),\n"
            "sparse emojis, skimmable bullets, and a clear CTA. No markdown syntax—plain text.\n"
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
        f"Style Brief:\n{_style_prompt(style_summary)}\n\n"
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
            'persona_name': (persona_obj or {}).get('name') if humanize else None
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