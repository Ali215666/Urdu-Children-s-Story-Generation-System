"""
FastAPI service for Urdu story generation using BPE tokenizer and trigram model
"""
import sys
sys.path.append('../tokenizer')
sys.path.append('../model')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bpe_tokenizer import load_tokenizer, encode
from trigram_model import load_model, generate_story

# Initialize FastAPI app
app = FastAPI(title="Urdu Story Generator API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models at startup
print("Loading models...")
vocab, merges = load_tokenizer('../tokenizer')
unigrams, bigrams, trigrams = load_model('../model/trigram_model.pkl')
print("✓ Models loaded successfully")


# Request/Response models
class GenerateRequest(BaseModel):
    prefix: str = Field(..., description="Starting text for story generation")
    max_length: int = Field(50, ge=1, le=200, description="Maximum number of tokens to generate")


class GenerateResponse(BaseModel):
    story: str


@app.post("/generate", response_model=GenerateResponse)
def generate_story_endpoint(request: GenerateRequest):
    """
    Generate Urdu story from given prefix using trigram language model.
    
    Args:
        prefix: Starting text (Urdu words separated by spaces)
        max_length: Maximum number of tokens to generate
        
    Returns:
        Generated story as string
    """
    # Encode prefix with BPE tokenizer
    prefix_tokens = encode(request.prefix, merges)
    
    # Generate story tokens with trigram model
    story_text = generate_story(
        prefix_tokens=prefix_tokens,
        max_len=request.max_length,
        unigram_counts=unigrams,
        bigram_counts=bigrams,
        trigram_counts=trigrams
    )
    
    print(f"DEBUG - Raw story before cleaning: {repr(story_text)}")
    
    # Ensure story_text is a string
    if story_text is None:
        story_text = ""
    else:
        story_text = str(story_text)
    
    # Clean up the story text - remove all special tokens and undefined
    special_tokens = [
        '<EOT>', '<EOS>', '<EOP>', '<PAD>', 
        'undefined', 'None', 'null', 'NaN',
        '<UNK>', '<START>', '<END>'
    ]
    
    for token in special_tokens:
        story_text = story_text.replace(token, '')
    
    # Remove any remaining angle bracket tokens
    import re
    story_text = re.sub(r'<[^>]+>', '', story_text)
    
    # Clean up extra spaces and strip
    story_text = ' '.join(story_text.split())
    story_text = story_text.strip()
    
    print(f"DEBUG - Cleaned story: {repr(story_text)}")
    
    return GenerateResponse(story=story_text)


@app.get("/")
def root():
    """API health check"""
    return {
        "status": "running",
        "service": "Urdu Story Generator",
        "vocab_size": len(unigrams),
        "bigrams": len(bigrams),
        "trigrams": len(trigrams)
    }


# Run with: python api.py
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("Starting Urdu Story Generator API")
    print("="*70)
    print("\nAPI Endpoints:")
    print("  GET  / - Health check")
    print("  POST /generate - Generate story")
    print("\nExample request:")
    print('  curl -X POST "http://localhost:8000/generate" \\')
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"prefix": "ایک دن", "max_length": 30}\'')
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
