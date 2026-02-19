"""
Trigram Language Model for Urdu Story Generation
- N-gram counting (unigrams, bigrams, trigrams)
- Interpolated probability smoothing
- Story generation using BPE tokens
"""

import pickle
import random
import sys
import os
from collections import defaultdict
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tokenizer'))

from utils.constants import EOS, EOP, EOT, SPECIAL_TOKENS, EOW
from bpe_tokenizer import decode  # type: ignore


def count_ngrams(tokens: List[str]) -> Tuple[Dict[str, int], Dict[Tuple[str, str], int], Dict[Tuple[str, str, str], int]]:
    """
    Count unigrams, bigrams, and trigrams from a token list.
    
    Args:
        tokens: List of tokens from tokenized text
        
    Returns:
        Tuple of (unigram_counts, bigram_counts, trigram_counts)
        - unigram_counts: Dict mapping single tokens to counts
        - bigram_counts: Dict mapping token pairs to counts
        - trigram_counts: Dict mapping token triples to counts
        
    Example:
        >>> tokens = ['ا', 'ب', 'ت', '</w>', 'اچھا</w>']
        >>> uni, bi, tri = count_ngrams(tokens)
        >>> uni['ا']  # 1
        >>> bi[('ا', 'ب')]  # 1
        >>> tri[('ا', 'ب', 'ت')]  # 1
    """
    unigram_counts = defaultdict(int)
    bigram_counts = defaultdict(int)
    trigram_counts = defaultdict(int)
    
    # Count all n-grams in a single pass
    for i in range(len(tokens)):
        # Unigram
        unigram_counts[tokens[i]] += 1
        
        # Bigram
        if i < len(tokens) - 1:
            bigram = (tokens[i], tokens[i + 1])
            bigram_counts[bigram] += 1
        
        # Trigram
        if i < len(tokens) - 2:
            trigram = (tokens[i], tokens[i + 1], tokens[i + 2])
            trigram_counts[trigram] += 1
    
    return dict(unigram_counts), dict(bigram_counts), dict(trigram_counts)


def compute_trigram_probabilities(
    unigram_counts: Dict[str, int],
    bigram_counts: Dict[Tuple[str, str], int],
    trigram_counts: Dict[Tuple[str, str, str], int]
) -> Dict[Tuple[str, str], Dict[str, float]]:
    """
    Compute trigram probabilities using Maximum Likelihood Estimation (MLE).
    
    Formula: P(w3 | w1, w2) = C(w1, w2, w3) / C(w1, w2)
    
    Args:
        unigram_counts: Dictionary of single token counts
        bigram_counts: Dictionary of token pair counts
        trigram_counts: Dictionary of token triple counts
        
    Returns:
        Dictionary mapping context (w1, w2) to probability distribution over next token w3
        Structure: {(w1, w2): {w3: probability, ...}, ...}
        
    Example:
        >>> tri = {('a', 'b', 'c'): 3, ('a', 'b', 'd'): 1}
        >>> bi = {('a', 'b'): 4}
        >>> probs = compute_trigram_probabilities({}, bi, tri)
        >>> probs[('a', 'b')]['c']  # 0.75
        >>> probs[('a', 'b')]['d']  # 0.25
    """
    trigram_probs = defaultdict(dict)
    
    # For each trigram, compute its probability given the bigram context
    for (w1, w2, w3), trigram_count in trigram_counts.items():
        context = (w1, w2)
        bigram_count = bigram_counts.get(context, 0)
        
        # Avoid division by zero
        if bigram_count > 0:
            probability = trigram_count / bigram_count
            trigram_probs[context][w3] = probability
    
    return dict(trigram_probs)


def interpolated_probability(
    w1: str,
    w2: str,
    w3: str,
    unigram_counts: Dict[str, int],
    bigram_counts: Dict[Tuple[str, str], int],
    trigram_counts: Dict[Tuple[str, str, str], int],
    lambdas: Tuple[float, float, float] = (0.1, 0.3, 0.6)
) -> float:
    """
    Compute interpolated trigram probability with linear interpolation smoothing.
    
    Formula: P_interp(w3 | w1, w2) = λ1*P1(w3) + λ2*P2(w3|w2) + λ3*P3(w3|w1,w2)
    
    Args:
        w1: First context word
        w2: Second context word
        w3: Target word
        unigram_counts: Dictionary of single token counts
        bigram_counts: Dictionary of token pair counts
        trigram_counts: Dictionary of token triple counts
        lambdas: Tuple of (λ1, λ2, λ3) weights, must sum to 1.0
        
    Returns:
        Interpolated probability as float
        
    Example:
        >>> uni = {'a': 10, 'b': 5, 'c': 3}
        >>> bi = {('a', 'b'): 4, ('b', 'c'): 2}
        >>> tri = {('a', 'b', 'c'): 2}
        >>> p = interpolated_probability('a', 'b', 'c', uni, bi, tri)
        >>> # λ1*P(c) + λ2*P(c|b) + λ3*P(c|a,b)
        >>> # 0.1*(3/18) + 0.3*(2/5) + 0.6*(2/4) = 0.437
    """
    lambda1, lambda2, lambda3 = lambdas
    
    # P1(w3) = C(w3) / total_unigrams
    total_unigrams = sum(unigram_counts.values())
    p1 = unigram_counts.get(w3, 0) / total_unigrams if total_unigrams > 0 else 0.0
    
    # P2(w3|w2) = C(w2, w3) / C(w2)
    bigram_w2_w3_count = bigram_counts.get((w2, w3), 0)
    w2_count = unigram_counts.get(w2, 0)
    p2 = bigram_w2_w3_count / w2_count if w2_count > 0 else 0.0
    
    # P3(w3|w1,w2) = C(w1, w2, w3) / C(w1, w2)
    trigram_count = trigram_counts.get((w1, w2, w3), 0)
    bigram_w1_w2_count = bigram_counts.get((w1, w2), 0)
    p3 = trigram_count / bigram_w1_w2_count if bigram_w1_w2_count > 0 else 0.0
    
    # Interpolate
    return lambda1 * p1 + lambda2 * p2 + lambda3 * p3


def generate_story(
    prefix_tokens: List[str],
    max_len: int,
    unigram_counts: Dict[str, int],
    bigram_counts: Dict[Tuple[str, str], int],
    trigram_counts: Dict[Tuple[str, str, str], int],
    lambdas: Tuple[float, float, float] = (0.1, 0.3, 0.6)
) -> str:
    """
    Generate story text using trigram language model with interpolation smoothing.
    Generation stops when EOT token is produced.
    
    Args:
        prefix_tokens: Initial tokens to start generation (at least 2 tokens)
        max_len: Maximum number of tokens to generate
        unigram_counts: Dictionary of single token counts
        bigram_counts: Dictionary of token pair counts
        trigram_counts: Dictionary of token triple counts
        lambdas: Interpolation weights (λ1, λ2, λ3)
        
    Returns:
        Generated story as string (special tokens removed)
        
    Example:
        >>> prefix = ['وہ</w>', 'گھر</w>']
        >>> story = generate_story(prefix, 20, uni, bi, tri)
        >>> # Returns decoded story text
    """
    tokens = prefix_tokens.copy()
    
    # Get all possible next tokens from vocabulary
    vocab = list(unigram_counts.keys())
    
    # Generate tokens until max_len or EOT is reached
    while len(tokens) < max_len:
        # Get last two tokens as context
        if len(tokens) >= 2:
            w1, w2 = tokens[-2], tokens[-1]
        elif len(tokens) == 1:
            # Not enough context, use dummy token
            w1, w2 = '<PAD>', tokens[-1]
        else:
            # Empty prefix, shouldn't happen but handle gracefully
            break
        
        # Compute probability for each candidate next token
        probs = []
        candidates = []
        
        for w3 in vocab:
            p = interpolated_probability(w1, w2, w3, unigram_counts, bigram_counts, trigram_counts, lambdas)
            if p > 0:  # Only consider tokens with non-zero probability
                probs.append(p)
                candidates.append(w3)
        
        # If no valid candidates, stop generation
        if not candidates:
            break
        
        # Sample next token using probability distribution
        next_token = random.choices(candidates, weights=probs, k=1)[0]
        tokens.append(next_token)
        
        # Stop at end-of-text token (required by spec)
        if next_token == EOT:
            break
        
        # Optional: also stop at end-of-sentence if we want shorter outputs
        # (commented out to allow full story generation)
        # if next_token == EOS:
        #     break
    
    # Ensure story ends properly with EOT
    # If we stopped due to max_length, add EOT for proper completion
    if len(tokens) >= max_len and tokens[-1] != EOT:
        tokens.append(EOT)
    
    # Decode tokens to text (special tokens are filtered in decode())
    decoded_text = decode(tokens)
    
    # Ensure the decoded text ends with proper Urdu punctuation
    # This prevents stories from looking incomplete
    if decoded_text:
        decoded_text = decoded_text.rstrip()
        # Check if it ends with Urdu sentence-ending punctuation
        if not decoded_text.endswith(('۔', '؟', '!')):
            decoded_text += '۔'  # Add Urdu period
    
    # Extra safety: ensure we return a clean string
    if decoded_text is None:
        decoded_text = ""
    
    return str(decoded_text).strip()


def save_model(
    model_path: str,
    unigram_counts: Dict[str, int],
    bigram_counts: Dict[Tuple[str, str], int],
    trigram_counts: Dict[Tuple[str, str, str], int]
) -> None:
    """
    Save n-gram counts to disk using pickle.
    
    Args:
        model_path: Path to save the model file
        unigram_counts: Dictionary of single token counts
        bigram_counts: Dictionary of token pair counts
        trigram_counts: Dictionary of token triple counts
    """
    model_data = {
        'unigrams': unigram_counts,
        'bigrams': bigram_counts,
        'trigrams': trigram_counts
    }
    
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"✓ Model saved to: {model_path}")


def load_model(model_path: str) -> Tuple[Dict[str, int], Dict[Tuple[str, str], int], Dict[Tuple[str, str, str], int]]:
    """
    Load n-gram counts from disk.
    
    Args:
        model_path: Path to the saved model file
        
    Returns:
        Tuple of (unigram_counts, bigram_counts, trigram_counts)
    """
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    print(f"✓ Model loaded from: {model_path}")
    print(f"  Unigrams: {len(model_data['unigrams']):,}")
    print(f"  Bigrams:  {len(model_data['bigrams']):,}")
    print(f"  Trigrams: {len(model_data['trigrams']):,}")
    
    return model_data['unigrams'], model_data['bigrams'], model_data['trigrams']


if __name__ == "__main__":
    # Test with sample token list
    print("Testing N-gram Counter")
    print("=" * 60)
    
    # Sample tokens from BPE encoding
    test_tokens = ['بہت</w>', 'اچھ', 'ا</w>', 'دن</w>', 'تھ', 'ا</w>']
    
    print(f"\nInput tokens: {test_tokens}")
    print(f"Total tokens: {len(test_tokens)}\n")
    
    # Count n-grams
    unigrams, bigrams, trigrams = count_ngrams(test_tokens)
    
    # Display unigrams
    print("UNIGRAMS:")
    print("-" * 60)
    for token, count in unigrams.items():
        print(f"  {token:<20} → {count}")
    print(f"Total unique unigrams: {len(unigrams)}")
    
    # Display bigrams
    print("\nBIGRAMS:")
    print("-" * 60)
    for bigram, count in bigrams.items():
        token1, token2 = bigram
        print(f"  ({token1:<15}, {token2:<15}) → {count}")
    print(f"Total unique bigrams: {len(bigrams)}")
    
    # Display trigrams
    print("\nTRIGRAMS:")
    print("-" * 60)
    for trigram, count in trigrams.items():
        token1, token2, token3 = trigram
        print(f"  ({token1:<10}, {token2:<10}, {token3:<10}) → {count}")
    print(f"Total unique trigrams: {len(trigrams)}")
    
    print("\n" + "=" * 60)
    print("✓ N-gram counting test complete!")
    print("=" * 60)
    
    # Test trigram probabilities
    print("\n" + "=" * 60)
    print("Testing Trigram Probability Computation")
    print("=" * 60)
    
    # Compute probabilities from the counts
    trigram_probs = compute_trigram_probabilities(unigrams, bigrams, trigrams)
    
    print(f"\nNumber of contexts (bigrams with following tokens): {len(trigram_probs)}")
    
    # Show sample probability distributions
    print("\nSample probability distributions:")
    print("-" * 60)
    for i, (context, next_token_probs) in enumerate(list(trigram_probs.items())[:3]):
        w1, w2 = context
        print(f"\nContext: ({w1}, {w2})")
        for w3, prob in next_token_probs.items():
            print(f"  P({w3} | {w1}, {w2}) = {prob:.4f}")
        # Verify probabilities sum to 1.0
        total_prob = sum(next_token_probs.values())
        print(f"  Sum of probabilities: {total_prob:.4f}")
    
    # Additional test with simple example
    print("\n" + "=" * 60)
    print("Testing with simple example:")
    print("=" * 60)
    
    # Create simple test case
    test_tri = {('a', 'b', 'c'): 3, ('a', 'b', 'd'): 1}
    test_bi = {('a', 'b'): 4}
    test_uni = {'a': 4, 'b': 4, 'c': 3, 'd': 1}
    
    test_probs = compute_trigram_probabilities(test_uni, test_bi, test_tri)
    
    print("Trigrams: {('a', 'b', 'c'): 3, ('a', 'b', 'd'): 1}")
    print("Bigrams:  {('a', 'b'): 4}")
    print("\nComputed probabilities:")
    for context, next_probs in test_probs.items():
        print(f"  Context {context}:")
        for token, prob in next_probs.items():
            print(f"    P({token} | {context}) = {prob:.4f}")
    
    print("\n" + "=" * 60)
    print("✓ Trigram probability computation test complete!")
    print("=" * 60)
    
    # Test interpolated probability
    print("\n" + "=" * 60)
    print("Testing Interpolated Probability (Smoothing)")
    print("=" * 60)
    
    # Use simple example: uni = {a:10, b:5, c:3}, bi = {(a,b):4, (b,c):2}, tri = {(a,b,c):2}
    test_uni = {'a': 10, 'b': 5, 'c': 3}
    test_bi = {('a', 'b'): 4, ('b', 'c'): 2}
    test_tri = {('a', 'b', 'c'): 2}
    
    print("\nCounts:")
    print(f"  Unigrams: {test_uni}")
    print(f"  Bigrams:  {test_bi}")
    print(f"  Trigrams: {test_tri}")
    
    # Compute interpolated probability
    p_interp = interpolated_probability('a', 'b', 'c', test_uni, test_bi, test_tri)
    
    # Manual calculation for verification
    total = sum(test_uni.values())  # 18
    p1 = test_uni['c'] / total  # 3/18 = 0.1667
    p2 = test_bi[('b', 'c')] / test_uni['b']  # 2/5 = 0.4
    p3 = test_tri[('a', 'b', 'c')] / test_bi[('a', 'b')]  # 2/4 = 0.5
    
    print(f"\nλ = (0.1, 0.3, 0.6)")
    print(f"P1(c) = {p1:.4f}  (unigram: C(c)/total = 3/18)")
    print(f"P2(c|b) = {p2:.4f}  (bigram: C(b,c)/C(b) = 2/5)")
    print(f"P3(c|a,b) = {p3:.4f}  (trigram: C(a,b,c)/C(a,b) = 2/4)")
    
    expected = 0.1 * p1 + 0.3 * p2 + 0.6 * p3
    print(f"\nP_interp(c|a,b) = 0.1*{p1:.4f} + 0.3*{p2:.4f} + 0.6*{p3:.4f}")
    print(f"                = {expected:.4f}")
    print(f"Function result = {p_interp:.4f}")
    print(f"Match: {'✓' if abs(p_interp - expected) < 0.0001 else '✗'}")
    
    # Test with unseen trigram (should fall back to bigram and unigram)
    p_unseen = interpolated_probability('a', 'b', 'd', test_uni, test_bi, test_tri)
    print(f"\nUnseen trigram (a,b,d): P_interp = {p_unseen:.4f}")
    print(f"  (Falls back to unigram since d not in vocabulary)")
    
    print("\n" + "=" * 60)
    print("✓ Interpolated probability test complete!")
    print("=" * 60)
    
    # Test story generation
    print("\n" + "=" * 60)
    print("Testing Story Generation")
    print("=" * 60)
    
    # Create richer test data for generation
    gen_uni = {'a': 10, 'b': 8, 'c': 6, 'd': 4, '<EOT>': 2}
    gen_bi = {
        ('a', 'b'): 6, ('b', 'c'): 5, ('c', 'd'): 4,
        ('d', 'a'): 3, ('b', 'd'): 2, ('d', '<EOT>'): 2
    }
    gen_tri = {
        ('a', 'b', 'c'): 4, ('b', 'c', 'd'): 3,
        ('c', 'd', 'a'): 2, ('d', 'a', 'b'): 2,
        ('b', 'd', '<EOT>'): 1, ('c', 'd', '<EOT>'): 1
    }
    
    print("\nGenerating short sequences with prefix ['a', 'b']:")
    print("-" * 60)
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate 3 sample stories
    for i in range(3):
        prefix = ['a', 'b']
        story = generate_story(prefix, max_len=10, 
                              unigram_counts=gen_uni, 
                              bigram_counts=gen_bi, 
                              trigram_counts=gen_tri)
        print(f"  {i+1}. Generated: {story}")
    
    print("\n" + "=" * 60)
    print("✓ Story generation test complete!")
    print("=" * 60)
    
    # Test save and load model
    print("\n" + "=" * 60)
    print("Testing Model Save/Load")
    print("=" * 60)
    
    # Save the model
    model_file = "test_trigram_model.pkl"
    print(f"\nSaving model to '{model_file}'...")
    save_model(model_file, gen_uni, gen_bi, gen_tri)
    
    # Load it back
    print(f"\nLoading model from '{model_file}'...")
    loaded_uni, loaded_bi, loaded_tri = load_model(model_file)
    
    # Verify by computing a probability
    print("\nVerification:")
    print("-" * 60)
    
    # Compare original and loaded counts
    print(f"Original unigrams: {len(gen_uni)}, Loaded: {len(loaded_uni)}")
    print(f"Original bigrams:  {len(gen_bi)}, Loaded: {len(loaded_bi)}")
    print(f"Original trigrams: {len(gen_tri)}, Loaded: {len(loaded_tri)}")
    
    # Test probability computation with both
    test_w1, test_w2, test_w3 = 'a', 'b', 'c'
    p_original = interpolated_probability(test_w1, test_w2, test_w3, gen_uni, gen_bi, gen_tri)
    p_loaded = interpolated_probability(test_w1, test_w2, test_w3, loaded_uni, loaded_bi, loaded_tri)
    
    print(f"\nP_interp({test_w3}|{test_w1},{test_w2}):")
    print(f"  Original model: {p_original:.4f}")
    print(f"  Loaded model:   {p_loaded:.4f}")
    print(f"  Match: {'✓' if abs(p_original - p_loaded) < 0.0001 else '✗'}")
    
    # Clean up test file
    import os
    os.remove(model_file)
    print(f"\n✓ Cleaned up test file: {model_file}")
    
    print("\n" + "=" * 60)
    print("✓ Model save/load test complete!")
    print("=" * 60)
