"""
Train BPE tokenizer on Urdu corpus and save results
"""
from bpe_tokenizer import (
    load_corpus, initialize_vocabulary, train_bpe, 
    count_unique_symbols, save_tokenizer, load_tokenizer
)
import json

# Configuration
CORPUS_PATH = "../Data/Preprocessed/corpus.txt"
TARGET_VOCAB_SIZE = 250
OUTPUT_DIR = "."

def main():
    print("="*60)
    print("BPE TOKENIZER TRAINING")
    print("="*60)
    
    # Load corpus
    print("\n1. Loading corpus...")
    words = load_corpus(CORPUS_PATH)
    print(f"   Loaded {len(words):,} words")
    
    # Initialize vocabulary
    print("\n2. Initializing character-level vocabulary...")
    vocab = initialize_vocabulary(words)
    print(f"   Unique word forms: {len(vocab):,}")
    print(f"   Initial symbol count: {count_unique_symbols(vocab)}")
    
    # Train BPE
    print(f"\n3. Training BPE (target vocab size: {TARGET_VOCAB_SIZE})...")
    print()
    final_vocab, merges = train_bpe(vocab, TARGET_VOCAB_SIZE)
    
    # Show example merges
    print(f"\n4. Example merge operations:")
    print("="*60)
    print("First 10 merges:")
    for i, (sym1, sym2) in enumerate(merges[:10], 1):
        merged = sym1 + sym2
        print(f"  {i:2d}. {sym1!r} + {sym2!r} → {merged!r}")
    
    if len(merges) > 10:
        print("\nLast 10 merges:")
        for i, (sym1, sym2) in enumerate(merges[-10:], len(merges)-9):
            merged = sym1 + sym2
            print(f"  {i:2d}. {sym1!r} + {sym2!r} → {merged!r}")
    
    # Show final vocabulary sample
    print(f"\n5. Final vocabulary samples:")
    print("="*60)
    print("Example tokenized words:")
    for i, (word_tuple, freq) in enumerate(list(final_vocab.items())[:10]):
        word_str = ' | '.join(word_tuple)
        print(f"  {word_str:<40} (freq: {freq})")
    
    # Statistics
    print(f"\n6. Final Statistics:")
    print("="*60)
    print(f"Total merges performed: {len(merges)}")
    print(f"Final vocabulary size: {count_unique_symbols(final_vocab)} symbols")
    print(f"Unique word forms: {len(final_vocab):,}")
    
    # Save tokenizer
    print(f"\n7. Saving tokenizer...")
    print("="*60)
    save_tokenizer(final_vocab, merges, OUTPUT_DIR)
    
    # Test loading
    print(f"\n8. Testing tokenizer reload...")
    print("="*60)
    loaded_vocab, loaded_merges = load_tokenizer(OUTPUT_DIR)
    
    # Verify loaded data matches
    print("\nVerifying loaded data:")
    if len(loaded_vocab) == len(final_vocab):
        print(f"  ✓ Vocabulary size matches: {len(loaded_vocab):,} word forms")
    else:
        print(f"  ✗ Vocabulary size mismatch!")
    
    if len(loaded_merges) == len(merges):
        print(f"  ✓ Merges count matches: {len(loaded_merges)} merges")
    else:
        print(f"  ✗ Merges count mismatch!")
    
    if count_unique_symbols(loaded_vocab) == count_unique_symbols(final_vocab):
        print(f"  ✓ Symbol count matches: {count_unique_symbols(loaded_vocab)} symbols")
    else:
        print(f"  ✗ Symbol count mismatch!")
    
    print("\n" + "="*60)
    print("✓ Training and saving complete!")
    print("="*60)

if __name__ == "__main__":
    main()
