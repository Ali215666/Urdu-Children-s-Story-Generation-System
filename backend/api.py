"""
FastAPI service for Urdu story generation using BPE tokenizer and trigram model
"""
import sys
import os

# Add parent and sibling directories to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tokenizer'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model'))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bpe_tokenizer import load_tokenizer, encode
from trigram_model import load_model, generate_story
from utils.constants import EOS, EOP, EOT, SPECIAL_TOKENS

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
tokenizer_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tokenizer')
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model', 'trigram_model.pkl')

vocab, merges = load_tokenizer(tokenizer_dir)
unigrams, bigrams, trigrams = load_model(model_path)
print("✓ Models loaded successfully")


# Request/Response models
class GenerateRequest(BaseModel):
    prefix: str = Field(..., description="Starting text for story generation")
    max_length: int = Field(500, ge=10, le=2000, description="Maximum number of tokens to generate")


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
        Generated story as string (special tokens are filtered by decode())
    """
    # Encode prefix with BPE tokenizer
    prefix_tokens = encode(request.prefix, merges)
    
    # Generate story tokens with trigram model
    # decode() function already filters out special tokens
    story_text = generate_story(
        prefix_tokens=prefix_tokens,
        max_len=request.max_length,
        unigram_counts=unigrams,
        bigram_counts=bigrams,
        trigram_counts=trigrams
    )
    
    # Ensure story_text is a string and clean
    if story_text is None:
        story_text = ""
    else:
        story_text = str(story_text).strip()
    
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
    
    uvicorn.run(app, host="localhost", port=8000)
