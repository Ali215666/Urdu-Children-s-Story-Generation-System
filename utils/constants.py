"""
Special tokens for Urdu Story Generator
Using Unicode Private Use Area characters (U+E000 - U+E002)
These are guaranteed not to appear in natural Urdu text
"""

# Special tokens as single Unicode characters
EOS = '\uE000'  # End of Sentence
EOP = '\uE001'  # End of Paragraph
EOT = '\uE002'  # End of Text/Story

# Set of all special tokens for easy checking
SPECIAL_TOKENS = {EOS, EOP, EOT}

# End-of-word marker for BPE
EOW = '</w>'

# Mapping for display/debugging purposes
TOKEN_NAMES = {
    EOS: 'EOS',
    EOP: 'EOP',
    EOT: 'EOT'
}

def is_special_token(token: str) -> bool:
    """Check if a token is a special token"""
    return token in SPECIAL_TOKENS
