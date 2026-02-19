import os
import re
import sys
from pathlib import Path

# Add parent directory to path for constants import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.constants import EOS, EOP, EOT

def normalize_urdu_text(text):
    """Normalize Unicode and standardize Urdu characters"""
    # Replace Arabic characters with Urdu equivalents
    text = text.replace('ي', 'ی')  # Arabic Yeh → Urdu Yeh
    text = text.replace('ك', 'ک')  # Arabic Kaf → Urdu Kaf
    text = text.replace('ى', 'ی')  # Alef Maksura → Urdu Yeh
    text = text.replace('ے', 'ے')  # Normalize Yeh Barree
    
    # Normalize different types of spaces
    text = text.replace('\u200c', '')  # Zero-width non-joiner
    text = text.replace('\u200d', '')  # Zero-width joiner
    text = text.replace('\xa0', ' ')   # Non-breaking space
    text = text.replace('\t', ' ')     # Tab to space
    
    return text

def remove_html_tags(text):
    """Remove any HTML tags if present"""
    return re.sub(r'<[^>]+>', '', text)

def clean_text(text):
    """Clean text by removing unwanted characters"""
    # Remove HTML tags
    text = remove_html_tags(text)
    
    # Normalize Unicode
    text = normalize_urdu_text(text)
    
    # Remove English letters (both uppercase and lowercase)
    text = re.sub(r'[A-Za-z]', '', text)
    
    # Remove numbers
    text = re.sub(r'[0-9]', '', text)
    
    # Remove English/special punctuation except those we want to keep
    # Keep: ۔ ؟ ! ، " " - and Urdu characters
    # Urdu Unicode ranges: \u0600-\u06FF (Arabic), \u0750-\u077F (Arabic Supplement), \uFB50-\uFDFF, \uFE70-\uFEFF
    # Keep spaces, newlines, and specific punctuation
    
    # First, protect the punctuation we want to keep by temporarily replacing them
    text = text.replace('۔', '<<<PERIOD>>>')
    text = text.replace('؟', '<<<QUESTION>>>')
    text = text.replace('!', '<<<EXCLAMATION>>>')
    text = text.replace('،', '<<<COMMA>>>')
    text = text.replace('"', '<<<QUOTE1>>>')
    text = text.replace('"', '<<<QUOTE2>>>')
    text = text.replace('"', '<<<QUOTE3>>>')
    text = text.replace('-', '<<<DASH>>>')
    text = text.replace('۔', '<<<PERIOD>>>')  # Different encoding
    
    # Remove all special characters except spaces and newlines
    # Keep Urdu script characters (Unicode ranges for Urdu/Arabic script)
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s<<<>>>A-Z]', '', text)
    
    # Restore protected punctuation
    text = text.replace('<<<PERIOD>>>', '۔')
    text = text.replace('<<<QUESTION>>>', '؟')
    text = text.replace('<<<EXCLAMATION>>>', '!')
    text = text.replace('<<<COMMA>>>', '،')
    text = text.replace('<<<QUOTE1>>>', '"')
    text = text.replace('<<<QUOTE2>>>', '"')
    text = text.replace('<<<QUOTE3>>>', '"')
    text = text.replace('<<<DASH>>>', '-')
    
    # Remove repeated punctuation
    text = re.sub(r'۔+', '۔', text)
    text = re.sub(r'؟+', '؟', text)
    text = re.sub(r'!+', '!', text)
    text = re.sub(r'،+', '،', text)
    
    # Normalize spaces (remove multiple spaces)
    text = re.sub(r' +', ' ', text)
    
    # Remove spaces at the beginning and end of lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text

def extract_story_content(file_path):
    """Extract story content, skipping metadata"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find where the actual story starts (after the === separator)
        story_start_idx = 0
        for i, line in enumerate(lines):
            if '=' * 10 in line:  # Separator line
                story_start_idx = i + 1
                break
        
        # Get story content (everything after separator)
        story_lines = lines[story_start_idx:]
        story_text = ''.join(story_lines)
        
        return story_text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def insert_special_tokens(text):
    """Insert EOS, EOP, and EOT tokens using unused Unicode Private Use Area characters.
    
    Using single Unicode codepoints (U+E000, U+E001, U+E002) instead of ASCII strings
    like <EOS> so that the BPE tokenizer treats each token as a single atomic unit.
    """
    # Split text into paragraphs (separated by empty lines)
    paragraphs = text.split('\n\n')
    
    processed_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Split paragraph into sentences based on Urdu punctuation
        # Sentence enders: ۔ ؟ !
        
        # Add EOS after each sentence-ending punctuation
        processed_para = paragraph
        
        # Replace each sentence-ending punctuation with itself + EOS + newline
        processed_para = re.sub(r'([۔؟!])\s*', r'\1' + EOS + '\n', processed_para)
        
        # Remove trailing newline and add EOP
        processed_para = processed_para.strip()
        if processed_para:
            processed_para += '\n' + EOP
            processed_paragraphs.append(processed_para)
    
    # Join all paragraphs
    result = '\n'.join(processed_paragraphs)
    
    # Add EOT at the very end
    if result:
        result += '\n' + EOT
    
    return result

def process_single_file(file_path):
    """Process a single story file"""
    # Extract story content (skip metadata)
    story_text = extract_story_content(file_path)
    if not story_text:
        return None
    
    # Clean the text
    cleaned_text = clean_text(story_text)
    
    # Remove empty lines that got created during cleaning
    # But preserve paragraph structure (double newlines)
    lines = cleaned_text.split('\n')
    
    # Reconstruct with paragraph breaks preserved
    result_lines = []
    prev_empty = False
    for line in lines:
        line = line.strip()
        if not line:
            if not prev_empty:  # Keep one empty line for paragraph break
                result_lines.append('')
            prev_empty = True
        else:
            result_lines.append(line)
            prev_empty = False
    
    cleaned_text = '\n'.join(result_lines).strip()
    
    # Insert special tokens
    processed_text = insert_special_tokens(cleaned_text)
    
    return processed_text

def process_all_stories(data_folder='data', output_file='all_stories.txt'):
    """Process all story files and combine them into one file"""
    print("Starting preprocessing of Urdu stories...")
    print("=" * 60)
    
    # Get all .txt files in the data folder
    data_path = Path(data_folder)
    if not data_path.exists():
        print(f"Error: Data folder '{data_folder}' not found!")
        return
    
    txt_files = sorted(list(data_path.glob('*.txt')))
    
    if not txt_files:
        print(f"No .txt files found in '{data_folder}' folder!")
        return
    
    print(f"Found {len(txt_files)} files to process\n")
    
    # Open output file for writing
    processed_count = 0
    skipped_count = 0
    
    with open(output_file, 'w', encoding='utf-8') as output:
        for i, file_path in enumerate(txt_files, 1):
            print(f"[{i}/{len(txt_files)}] Processing: {file_path.name}")
            
            # Process the file
            processed_text = process_single_file(file_path)
            
            if processed_text:
                # Write to output file
                output.write(processed_text)
                output.write('\n')  # Add extra newline between stories
                processed_count += 1
                print(f"  ✓ Successfully processed")
            else:
                skipped_count += 1
                print(f"  ✗ Skipped (error or empty)")
    
    print("\n" + "=" * 60)
    print(f"Preprocessing complete!")
    print(f"  Successfully processed: {processed_count} files")
    print(f"  Skipped: {skipped_count} files")
    print(f"  Output saved to: {output_file}")
    print("=" * 60)

def main():
    """Main function"""
    # Configuration
    data_folder = 'data'
    output_file = 'all_stories.txt'
    
    # Process all stories
    process_all_stories(data_folder, output_file)
    
    # Show sample of output
    print("\nFirst 500 characters of output:")
    print("-" * 60)
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            sample = f.read(500)
            print(sample)
            if len(sample) == 500:
                print("...")
    except Exception as e:
        print(f"Could not read output file: {e}")

if __name__ == "__main__":
    main()
