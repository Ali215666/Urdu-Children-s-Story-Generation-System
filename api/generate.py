"""
Vercel Serverless Function for Urdu Story Generation
Handles POST requests to /api/generate

This function:
1. Loads the trigram model and BPE tokenizer at cold start
2. Accepts JSON: {"prefix": "ایک دن", "max_length": 500}
3. Generates story using trigram model until EOT token
4. Returns JSON: {"story": "generated text"}
"""

import json
import sys
import os

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'tokenizer'))
sys.path.insert(0, os.path.join(parent_dir, 'model'))
sys.path.insert(0, os.path.join(parent_dir, 'utils'))

# Import project modules
from tokenizer.bpe_tokenizer import load_tokenizer, encode
from model.trigram_model import load_model, generate_story
from utils.constants import EOS, EOP, EOT, SPECIAL_TOKENS

# Global variables for model caching (persists across warm starts)
_vocab = None
_merges = None
_unigrams = None
_bigrams = None
_trigrams = None


def load_models():
    """
    Load tokenizer and trigram model (cached after first cold start).
    Vercel keeps these in memory for subsequent requests (warm starts).
    """
    global _vocab, _merges, _unigrams, _bigrams, _trigrams
    
    if _vocab is None:
        print("🔄 Cold start: Loading models...")
        
        # Construct paths relative to project root
        tokenizer_dir = os.path.join(parent_dir, 'tokenizer')
        model_path = os.path.join(parent_dir, 'model', 'trigram_model.pkl')
        
        # Load tokenizer
        _vocab, _merges = load_tokenizer(tokenizer_dir)
        print(f"✓ Tokenizer loaded: {len(_vocab)} vocab items")
        
        # Load trigram model
        _unigrams, _bigrams, _trigrams = load_model(model_path)
        print(f"✓ Model loaded: {len(_unigrams)} unigrams, {len(_bigrams)} bigrams, {len(_trigrams)} trigrams")
    
    return _vocab, _merges, _unigrams, _bigrams, _trigrams


def handler(event, context):
    """
    Vercel serverless function handler.
    
    Args:
        event: Request object containing HTTP method, body, headers
        context: Runtime context (unused)
    
    Returns:
        Response object with statusCode, body, headers
    """
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS' or event.get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Content-Type': 'application/json'
                },
                'body': ''
            }
        
        # Get request body
        body = event.get('body', '')
        if isinstance(body, str):
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return error_response(400, "Invalid JSON in request body")
        else:
            data = body
        
        # Validate input
        prefix = data.get('prefix', '').strip()
        if not prefix:
            return error_response(400, "Missing or empty 'prefix' field")
        
        max_length = data.get('max_length', 500)
        try:
            max_length = int(max_length)
            if max_length < 10 or max_length > 2000:
                raise ValueError()
        except ValueError:
            return error_response(400, "max_length must be an integer between 10 and 2000")
        
        # Load models (cached after first request)
        vocab, merges, unigrams, bigrams, trigrams = load_models()
        
        # Encode prefix with BPE tokenizer
        prefix_tokens = encode(prefix, merges)
        print(f"📝 Prefix: '{prefix}' → {len(prefix_tokens)} tokens")
        
        # Generate story using trigram model
        story_text = generate_story(
            prefix_tokens=prefix_tokens,
            max_len=max_length,
            unigram_counts=unigrams,
            bigram_counts=bigrams,
            trigram_counts=trigrams
        )
        
        # Ensure we have a valid string
        if story_text is None:
            story_text = ""
        else:
            story_text = str(story_text).strip()
        
        print(f"✓ Generated {len(story_text)} characters")
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'story': story_text,
                'prefix': prefix,
                'tokens_generated': len(story_text.split())
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(500, f"Internal server error: {str(e)}")


def error_response(status_code, message):
    """Helper to create error responses"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'status': status_code
        })
    }
