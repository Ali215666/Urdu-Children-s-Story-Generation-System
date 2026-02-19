"""
Train Trigram Language Model on tokenized corpus and save model
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tokenizer'))

from bpe_tokenizer import load_corpus, load_tokenizer, encode  # type: ignore
from trigram_model import count_ngrams, save_model  # type: ignore
from utils.constants import EOS, EOP, EOT, SPECIAL_TOKENS  # type: ignore

# Configuration
CORPUS_PATH = "data/processed/corpus.txt"
TOKENIZER_DIR = "tokenizer"
MODEL_OUTPUT_PATH = "model/trigram_model.pkl"

def main():
    print("="*70)
    print("TRIGRAM LANGUAGE MODEL TRAINING")
    print("="*70)
    
    # 1. Load corpus
    print("\n1. Loading corpus...")
    words = load_corpus(CORPUS_PATH)
    print(f"   Loaded {len(words):,} words")
    
    # Count special tokens in corpus
    eos_count = sum(1 for w in words if w == EOS)
    eop_count = sum(1 for w in words if w == EOP)
    eot_count = sum(1 for w in words if w == EOT)
    
    print(f"   Special tokens found:")
    print(f"     EOS: {eos_count:,}")
    print(f"     EOP: {eop_count:,}")
    print(f"     EOT: {eot_count:,}")
    
    # 2. Load trained BPE tokenizer
    print("\n2. Loading BPE tokenizer...")
    vocab, merges = load_tokenizer(TOKENIZER_DIR)
    print(f"   Tokenizer loaded with {len(merges)} merges")
    
    # 3. Tokenize entire corpus with BPE
    print("\n3. Tokenizing corpus with BPE...")
    text = ' '.join(words)
    tokens = encode(text, merges)
    print(f"   Total tokens after BPE: {len(tokens):,}")
    
    # Count special tokens in tokenized corpus
    eos_tok_count = sum(1 for t in tokens if t == EOS)
    eop_tok_count = sum(1 for t in tokens if t == EOP)
    eot_tok_count = sum(1 for t in tokens if t == EOT)
    
    print(f"   Special tokens in tokenized corpus:")
    print(f"     EOS: {eos_tok_count:,}")
    print(f"     EOP: {eop_tok_count:,}")
    print(f"     EOT: {eot_tok_count:,}")
    
    # 4. Count n-grams
    print("\n4. Counting n-grams...")
    unigrams, bigrams, trigrams = count_ngrams(tokens)
    
    print(f"   Unigrams: {len(unigrams):,}")
    print(f"   Bigrams:  {len(bigrams):,}")
    print(f"   Trigrams: {len(trigrams):,}")
    
    # Show special token counts in n-grams
    print(f"\n   Special tokens in unigram counts:")
    print(f"     EOS: {unigrams.get(EOS, 0):,}")
    print(f"     EOP: {unigrams.get(EOP, 0):,}")
    print(f"     EOT: {unigrams.get(EOT, 0):,}")
    
    # 5. Show sample statistics
    print("\n5. Sample n-gram statistics:")
    print("="*70)
    
    print("\n   Top 10 most frequent unigrams:")
    sorted_unigrams = sorted(unigrams.items(), key=lambda x: x[1], reverse=True)
    for i, (token, count) in enumerate(sorted_unigrams[:10], 1):
        # Display special tokens with names
        if token in SPECIAL_TOKENS:
            display = f"[{token.encode('unicode_escape').decode()}]"
        else:
            display = token
        print(f"     {i:2d}. {display:<20} → {count:,}")
    
    print("\n   Top 10 most frequent bigrams:")
    sorted_bigrams = sorted(bigrams.items(), key=lambda x: x[1], reverse=True)
    for i, (bigram, count) in enumerate(sorted_bigrams[:10], 1):
        t1, t2 = bigram
        # Display special tokens with names
        if t1 in SPECIAL_TOKENS:
            d1 = f"[{t1.encode('unicode_escape').decode()}]"
        else:
            d1 = t1
        if t2 in SPECIAL_TOKENS:
            d2 = f"[{t2.encode('unicode_escape').decode()}]"
        else:
            d2 = t2
        print(f"     {i:2d}. ({d1:<15}, {d2:<15}) → {count:,}")
    
    print("\n   Top 10 most frequent trigrams:")
    sorted_trigrams = sorted(trigrams.items(), key=lambda x: x[1], reverse=True)
    for i, (trigram, count) in enumerate(sorted_trigrams[:10], 1):
        t1, t2, t3 = trigram
        # Display special tokens with names
        if t1 in SPECIAL_TOKENS:
            d1 = f"[{t1.encode('unicode_escape').decode()}]"
        else:
            d1 = t1
        if t2 in SPECIAL_TOKENS:
            d2 = f"[{t2.encode('unicode_escape').decode()}]"
        else:
            d2 = t2
        if t3 in SPECIAL_TOKENS:
            d3 = f"[{t3.encode('unicode_escape').decode()}]"
        else:
            d3 = t3
        print(f"     {i:2d}. ({d1:<12}, {d2:<12}, {d3:<12}) → {count:,}")
    
    # 6. Save model
    print(f"\n6. Saving model to: {MODEL_OUTPUT_PATH}")
    print("="*70)
    save_model(MODEL_OUTPUT_PATH, unigrams, bigrams, trigrams)
    
    # 7. Verify save
    print(f"\n7. Verifying saved model...")
    from trigram_model import load_model
    loaded_uni, loaded_bi, loaded_tri = load_model(MODEL_OUTPUT_PATH)
    
    print("\n   Verification:")
    print(f"     ✓ Unigrams match: {len(loaded_uni) == len(unigrams)}")
    print(f"     ✓ Bigrams match:  {len(loaded_bi) == len(bigrams)}")
    print(f"     ✓ Trigrams match: {len(loaded_tri) == len(trigrams)}")
    
    print("\n" + "="*70)
    print("✓ Training complete!")
    print("="*70)

if __name__ == "__main__":
    main()
