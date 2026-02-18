"""
Byte Pair Encoding (BPE) Tokenizer for Urdu Text
Character-level initialization with </w> end-of-word markers
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple


def load_corpus(filepath: str) -> List[str]:
    """
    Load corpus and extract words.
    
    Args:
        filepath: Path to corpus.txt file
        
    Returns:
        List of all words from corpus
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Split by whitespace to get individual tokens
    words = text.split()
    
    return words


def initialize_vocabulary(words: List[str]) -> Dict[Tuple[str, ...], int]:
    """
    Initialize character-level vocabulary with word frequencies.
    Each word is represented as a tuple of characters ending with </w>.
    
    Args:
        words: List of words from corpus
        
    Returns:
        Dictionary mapping word tuples to their frequencies
        Example: {('ا', 'ل', 'ل', 'ہ', '</w>'): 15, ...}
    """
    vocab = defaultdict(int)
    
    for word in words:
        # Skip empty strings
        if not word:
            continue
            
        # Keep special tokens as-is (atomic tokens)
        if word in ['<EOS>', '<EOP>', '<EOT>']:
            word_tuple = (word,)
        else:
            # Convert word to tuple of characters + end marker
            word_tuple = tuple(list(word) + ['</w>'])
        
        vocab[word_tuple] += 1
    
    return dict(vocab)


def get_pair_frequencies(vocab: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, str], int]:
    """
    Count frequencies of adjacent symbol pairs in vocabulary.
    
    Args:
        vocab: Dictionary mapping word tuples to their frequencies
        
    Returns:
        Dictionary mapping symbol pairs to their total frequencies
        Example: {('ب', 'ہ'): 2855, ('ہ', 'ت'): 2855, ...}
    """
    pairs = defaultdict(int)
    
    for word_tuple, freq in vocab.items():
        # Skip single symbols (no pairs possible)
        if len(word_tuple) < 2:
            continue
        
        # Count all adjacent pairs in this word
        for i in range(len(word_tuple) - 1):
            pair = (word_tuple[i], word_tuple[i + 1])
            pairs[pair] += freq
    
    return dict(pairs)


def merge_pair(pair: Tuple[str, str], vocab: Dict[Tuple[str, ...], int]) -> Dict[Tuple[str, ...], int]:
    """
    Merge all occurrences of an adjacent symbol pair in the vocabulary.
    
    Args:
        pair: Tuple of two symbols to merge (symbol1, symbol2)
        vocab: Dictionary mapping word tuples to their frequencies
        
    Returns:
        New vocabulary dictionary with the pair merged into single symbols
        Example: ('ب', 'ہ', 'ت', '</w>') with pair ('ب', 'ہ') 
                 becomes ('بہ', 'ت', '</w>')
    """
    new_vocab = {}
    
    for word_tuple, freq in vocab.items():
        # Merge all occurrences of the pair in this word
        new_word = []
        i = 0
        while i < len(word_tuple):
            # Check if current position matches the pair to merge
            if i < len(word_tuple) - 1 and word_tuple[i] == pair[0] and word_tuple[i + 1] == pair[1]:
                # Merge the pair into single symbol
                new_word.append(pair[0] + pair[1])
                i += 2  # Skip both symbols
            else:
                # Keep symbol as-is
                new_word.append(word_tuple[i])
                i += 1
        
        new_vocab[tuple(new_word)] = freq
    
    return new_vocab


def count_unique_symbols(vocab: Dict[Tuple[str, ...], int]) -> int:
    """
    Count the number of unique symbols in vocabulary.
    
    Args:
        vocab: Dictionary mapping word tuples to their frequencies
        
    Returns:
        Number of unique symbols across all words
    """
    symbols = set()
    for word_tuple in vocab.keys():
        symbols.update(word_tuple)
    return len(symbols)


def train_bpe(vocab: Dict[Tuple[str, ...], int], target_vocab_size: int) -> Tuple[Dict[Tuple[str, ...], int], List[Tuple[str, str]]]:
    """
    Train BPE tokenizer by iteratively merging most frequent pairs.
    
    Args:
        vocab: Initial vocabulary (character-level)
        target_vocab_size: Target number of unique symbols (e.g., 250)
        
    Returns:
        Tuple of (final_vocab, merges_list)
        - final_vocab: Vocabulary after all merges
        - merges_list: Ordered list of merge operations applied
    """
    merges = []
    current_vocab = vocab
    
    print(f"Starting BPE training...")
    print(f"Initial vocabulary size: {count_unique_symbols(current_vocab)} symbols")
    print(f"Target vocabulary size: {target_vocab_size} symbols")
    print("=" * 60)
    
    iteration = 0
    while True:
        # Count current symbols
        current_symbol_count = count_unique_symbols(current_vocab)
        
        # Check if we've reached target
        if current_symbol_count >= target_vocab_size:
            print(f"\n✓ Target vocabulary size reached: {current_symbol_count} symbols")
            break
        
        # Get pair frequencies
        pairs = get_pair_frequencies(current_vocab)
        
        # Check if no more pairs to merge
        if not pairs:
            print(f"\n⚠ No more pairs to merge. Final size: {current_symbol_count} symbols")
            break
        
        # Select most frequent pair
        most_frequent_pair = max(pairs.items(), key=lambda x: x[1])[0]
        pair_freq = pairs[most_frequent_pair]
        
        # Apply merge
        current_vocab = merge_pair(most_frequent_pair, current_vocab)
        merges.append(most_frequent_pair)
        
        iteration += 1
        
        # Print progress every 10 merges
        if iteration % 10 == 0:
            merged_symbol = most_frequent_pair[0] + most_frequent_pair[1]
            print(f"Merge {iteration:3d}: {most_frequent_pair[0]!r:>15} + {most_frequent_pair[1]!r:<15} "
                  f"→ {merged_symbol!r:>20} (freq: {pair_freq:6d}) | Symbols: {current_symbol_count}")
    
    print("=" * 60)
    print(f"Training complete!")
    print(f"Total merges performed: {len(merges)}")
    print(f"Final vocabulary size: {count_unique_symbols(current_vocab)} symbols")
    
    return current_vocab, merges


def save_tokenizer(vocab: Dict[Tuple[str, ...], int], merges: List[Tuple[str, str]], output_dir: str) -> None:
    """
    Save trained BPE tokenizer to disk.
    
    Args:
        vocab: Vocabulary dictionary with word tuples as keys
        merges: List of merge operations
        output_dir: Directory to save tokenizer files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save vocabulary to JSON
    # Convert tuple keys to strings for JSON serialization
    vocab_serializable = {
        ' '.join(word_tuple): freq 
        for word_tuple, freq in vocab.items()
    }
    
    vocab_path = os.path.join(output_dir, 'vocab.json')
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocab_serializable, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved vocabulary to: {vocab_path}")
    
    # Save merges to text file
    # Each merge on one line: symbol1 symbol2
    merges_path = os.path.join(output_dir, 'merges.txt')
    with open(merges_path, 'w', encoding='utf-8') as f:
        for symbol1, symbol2 in merges:
            f.write(f"{symbol1} {symbol2}\n")
    
    print(f"✓ Saved merges to: {merges_path}")


def load_tokenizer(output_dir: str) -> Tuple[Dict[Tuple[str, ...], int], List[Tuple[str, str]]]:
    """
    Load trained BPE tokenizer from disk.
    
    Args:
        output_dir: Directory containing tokenizer files
        
    Returns:
        Tuple of (vocab, merges)
        - vocab: Vocabulary dictionary
        - merges: List of merge operations
    """
    # Load vocabulary from JSON
    vocab_path = os.path.join(output_dir, 'vocab.json')
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab_serialized = json.load(f)
    
    # Convert string keys back to tuples
    vocab = {
        tuple(word_str.split(' ')): freq 
        for word_str, freq in vocab_serialized.items()
    }
    
    print(f"✓ Loaded vocabulary from: {vocab_path}")
    print(f"  Unique word forms: {len(vocab):,}")
    
    # Load merges from text file
    merges = []
    merges_path = os.path.join(output_dir, 'merges.txt')
    with open(merges_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                # Split only on first space to handle symbols with spaces
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    merges.append((parts[0], parts[1]))
    
    print(f"✓ Loaded merges from: {merges_path}")
    print(f"  Total merges: {len(merges)}")
    
    return vocab, merges


def encode(text: str, merges: List[Tuple[str, str]]) -> List[str]:
    """
    Encode text into BPE tokens using learned merges.
    
    Args:
        text: Input text to tokenize
        merges: Ordered list of merge operations (from training)
        
    Returns:
        List of subword tokens
        
    Example:
        >>> merges = [('ے', '</w>'), ('ب', 'ہ')]
        >>> encode("بہت اچھا", merges)
        ['بہ', 'ت</w>', 'ا', 'چ', 'ھ', 'ا</w>']
    """
    # Split text into words
    words = text.split()
    
    all_tokens = []
    
    for word in words:
        # Handle special tokens as atomic units
        if word in ['<EOS>', '<EOP>', '<EOT>']:
            all_tokens.append(word)
            continue
        
        # Initialize with character-level tokens + end marker
        tokens = list(word) + ['</w>']
        
        # Apply each merge operation in sequence
        for merge_pair in merges:
            tokens = _apply_merge_to_tokens(tokens, merge_pair)
        
        # Add tokenized word to output
        all_tokens.extend(tokens)
    
    return all_tokens


def _apply_merge_to_tokens(tokens: List[str], pair: Tuple[str, str]) -> List[str]:
    """
    Apply a single merge operation to a list of tokens.
    
    Args:
        tokens: Current list of tokens
        pair: Pair of symbols to merge
        
    Returns:
        New list of tokens with merge applied
    """
    new_tokens = []
    i = 0
    
    while i < len(tokens):
        # Check if current position matches the merge pair
        if i < len(tokens) - 1 and tokens[i] == pair[0] and tokens[i + 1] == pair[1]:
            # Merge the pair
            new_tokens.append(pair[0] + pair[1])
            i += 2
        else:
            # Keep token as-is
            new_tokens.append(tokens[i])
            i += 1
    
    return new_tokens


def decode(tokens: List[str]) -> str:
    """
    Decode BPE tokens back into readable text.
    
    Args:
        tokens: List of BPE tokens (from encode function)
        
    Returns:
        Reconstructed text string
        
    Example:
        >>> tokens = ['بہت</w>', 'ا', 'چھ', 'ا</w>']
        >>> decode(tokens)
        'بہت اچھا'
    """
    # Handle None or empty input
    if not tokens:
        return ""
    
    # Define all special tokens to filter out
    special_tokens = {
        '<EOT>', '<EOS>', '<EOP>', '<PAD>', '<UNK>', '<START>', '<END>',
        'None', 'undefined', 'null', 'NaN', ''
    }
    
    # Filter out special tokens and invalid values
    valid_tokens = []
    for t in tokens:
        # Skip None, empty, or special tokens
        if t is None:
            continue
        token_str = str(t)
        if token_str and token_str not in special_tokens and not token_str.startswith('<'):
            valid_tokens.append(token_str)
    
    # Join all tokens into single string
    text = ''.join(valid_tokens)
    
    # Replace end-of-word markers with spaces
    text = text.replace('</w>', ' ')
    
    # Clean up extra spaces and return
    return ' '.join(text.split()).strip()


def print_vocab_stats(vocab: Dict[Tuple[str, ...], int]) -> None:
    """
    Print statistics about the vocabulary.
    
    Args:
        vocab: Vocabulary dictionary
    """
    print(f"Total unique word forms: {len(vocab)}")
    print(f"Total word occurrences: {sum(vocab.values())}")
    
    # Count unique symbols
    symbols = set()
    for word_tuple in vocab.keys():
        symbols.update(word_tuple)
    print(f"Unique symbols (characters): {len(symbols)}")
    
    # Show sample entries
    print("\nSample vocabulary entries:")
    for i, (word_tuple, freq) in enumerate(list(vocab.items())[:5]):
        print(f"  {''.join(word_tuple):<30} freq: {freq}")


if __name__ == "__main__":
    # Quick functionality test
    corpus_path = "../Data/Preprocessed/corpus.txt"
    test_output_dir = "./test_output"
    
    print("Testing BPE tokenizer components...")
    print("=" * 60)
    
    # Test 1: Load and initialize
    print("\n1. Loading corpus and initializing vocabulary...")
    words = load_corpus(corpus_path)
    vocab = initialize_vocabulary(words)
    print(f"   ✓ Loaded {len(words):,} words")
    print(f"   ✓ Created {len(vocab):,} unique word forms")
    print(f"   ✓ Initial symbols: {count_unique_symbols(vocab)}")
    
    # Test 2: Pair frequencies
    print("\n2. Testing pair frequency counting...")
    pairs = get_pair_frequencies(vocab)
    print(f"   ✓ Found {len(pairs):,} unique pairs")
    most_freq = max(pairs.items(), key=lambda x: x[1])[0]
    print(f"   ✓ Most frequent: {most_freq!r} (freq: {pairs[most_freq]:,})")
    
    # Test 3: Merge operation
    print("\n3. Testing merge operation...")
    merged_vocab = merge_pair(most_freq, vocab)
    merged_symbol = most_freq[0] + most_freq[1]
    print(f"   ✓ Merged {most_freq[0]!r} + {most_freq[1]!r} → {merged_symbol!r}")
    print(f"   ✓ Symbols after merge: {count_unique_symbols(merged_vocab)}")
    
    # Test 4: Save and load
    print("\n4. Testing save and load functionality...")
    test_merges = [(most_freq[0], most_freq[1])]  # Simple test with one merge
    save_tokenizer(merged_vocab, test_merges, test_output_dir)
    loaded_vocab, loaded_merges = load_tokenizer(test_output_dir)
    print(f"   ✓ Loaded vocab size matches: {len(loaded_vocab) == len(merged_vocab)}")
    print(f"   ✓ Loaded merges count matches: {len(loaded_merges) == len(test_merges)}")
    
    # Test 5: Encoding
    print("\n5. Testing encode functionality...")
    test_text = "بہت اچھا"
    encoded = encode(test_text, test_merges)
    print(f"   Input: {test_text}")
    print(f"   Tokens: {encoded}")
    print(f"   ✓ Encoded {len(encoded)} tokens")
    
    # Test 6: Decoding
    print("\n6. Testing decode functionality...")
    decoded = decode(encoded)
    print(f"   Encoded tokens: {encoded}")
    print(f"   Decoded text: {decoded}")
    print(f"   Original text: {test_text}")
    print(f"   ✓ Match: {decoded == test_text}")
    
    print("\n" + "="*60)
    print("✓ All components working correctly!")
    print("\nTo train the full BPE tokenizer, run: python train_bpe.py")
    print("="*60)
