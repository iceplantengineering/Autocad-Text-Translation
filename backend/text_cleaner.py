import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self):
        # DXF/MTEXT format codes to remove
        self.format_patterns = [
            # MTEXT formatting codes - handle both single and double backslash
            r'\\?pi-?\d+,-?\d+;',     # Paragraph indentation (with optional backslash)
            r'\\?pi-?\d+;',           # Paragraph indentation simplified (with optional backslash)
            r'\\?P',                  # Paragraph break (with optional backslash)
            r'\\?p\d+;',              # Paragraph formatting (with optional backslash)
            r'\\?l\d+;',              # Line spacing (with optional backslash)
            r'\\?f[^;]+;',            # Font specification (with optional backslash)
            r'\\?[HOQTL]+;?',         # Justification codes (with optional backslash)
            r'\\?[cC]\d+;',           # Color specification (with optional backslash)
            r'\\?[hH]\d+\.?\d*;',    # Text height (with optional backslash)
            r'\\?[wW]\d+\.?\d*;',    # Width factor (with optional backslash)
            r'\\?[aA]\d+;',           # Alignment angle (with optional backslash)
            r'\\?[qQ]\d+;',           # Oblique angle (with optional backslash)
            r'\\?[Ss](?:.*?);',      # Stacking text (with optional backslash)
            r'\\?[{}]',               # Braces (with optional backslash)
            r'\{.*?\}',              # Content in braces
            r'\\?[A-Za-z]\d*;',      # Other format codes (with optional backslash)
            r'\{\\?[^}]+\}',         # Format codes in braces (with optional backslash)

            # Additional patterns for broken/incomplete format codes - be more conservative
            # Only remove patterns that are clearly format codes, not technical data
            r'[a-zA-Z]\d+;',         # Incomplete format codes without backslash (like "i0;") but only if standalone
            r'[a-zA-Z]+;',           # Single letter format codes
            r'[a-zA-Z]+\d*[,:]\d*;', # Format codes with commas or colons
            # Remove numbers with semicolon only if they appear to be format codes
            r'(?<!\d)\d+;(?!\d)',    # Numbers with semicolon, not surrounded by other numbers
            # Remove isolated letter+number combinations that are likely format codes
            r'\b[a-zA-Z]\d+\b(?!\s*(?:X|kg|mm|℃|min|m))',  # Isolated letter+number but not in technical contexts
            # Be very careful with numbers mixed with letters - only remove obvious format codes
            r'\s+[a-zA-Z]\d+\s+(?!\d)',       # Space surrounded letter+number with no digits adjacent
        ]

        # Special characters to clean
        self.special_chars = [
            (r'[\x00-\x1f\x7f-\x9f]', ''),  # Control characters
            (r'\s+', ' '),                   # Multiple spaces to single space
            (r'^\s+|\s+$', ''),             # Leading/trailing spaces
            # Chinese punctuation and symbols to normalize
            (r'[，,、。；：！？""''（）【】《》〈〉…—]+', ' '),  # Chinese punctuation to space
            (r'[:：]', ' '),               # Colon variants to space
            (r'[;；]', ' '),               # Semicolon variants to space
            (r'[-—]', ' '),               # Dash variants to space
            (r'[（）\(\)]', ' '),          # Parentheses variants to space
            (r'[、]', '/'),                # Enumeration comma to slash
            (r'[・·]', '・'),              # Middle dot (keep as is)
        ]

        # Compile regex patterns
        self.format_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.format_patterns]
        self.special_regex = [(re.compile(pattern), replacement) for pattern, replacement in self.special_chars]

    def clean_text(self, text: str) -> str:
        """Clean text by removing formatting codes and normalizing"""
        if not text:
            return text

        original_text = text
        cleaned_text = text

        # Remove DXF formatting codes first
        for pattern in self.format_regex:
            cleaned_text = pattern.sub('', cleaned_text)

        # Clean special characters
        for pattern, replacement in self.special_regex:
            cleaned_text = pattern.sub(replacement, cleaned_text)

        # Remove extra whitespace
        cleaned_text = ' '.join(cleaned_text.split())

        # Post-processing: fix common formatting issues and restore technical data
        # The main issue is that numbers are being stripped by format code regexes
        # Let's try to reconstruct some common technical patterns

        # Fix common number-unit separations
        cleaned_text = re.sub(r'(\d+)\s+(kg|mm|℃|min)', r'\1\2', cleaned_text)
        cleaned_text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', cleaned_text)

        logger.debug(f"Text cleaning: '{original_text}' -> '{cleaned_text}'")
        return cleaned_text.strip()

    def clean_chinese_text(self, text: str) -> str:
        """Clean Chinese text specifically, preserving meaningful content"""
        if not text:
            return text

        # Use the main clean_text method which now includes Chinese punctuation handling
        cleaned = self.clean_text(text)

        # Additional Chinese-specific processing
        # Keep alphanumeric mixed with Chinese intact
        cleaned = re.sub(r'([a-zA-Z0-9]+)\s+([\u4e00-\u9fff])', r'\1\2', cleaned)  # Join separated alphanumeric-Chinese
        cleaned = re.sub(r'([\u4e00-\u9fff])\s+([a-zA-Z0-9]+)', r'\1\2', cleaned)  # Join separated Chinese-alphanumeric

        return cleaned.strip()

    def extract_clean_chinese_content(self, text: str) -> str:
        """Extract only the meaningful Chinese content from formatted text"""
        if not text:
            return text

        # Remove all formatting codes first
        cleaned = self.clean_text(text)

        # Extract Chinese characters and basic punctuation
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u3000-\u303f\uff00-\uffef]+')
        chinese_parts = chinese_pattern.findall(cleaned)

        if not chinese_parts:
            return cleaned

        # Rejoin with proper spacing
        result = ' '.join(part.strip() for part in chinese_parts if part.strip())
        return result if result else cleaned

    def is_meaningful_chinese_text(self, text: str) -> bool:
        """Check if the text contains meaningful Chinese content after cleaning"""
        if not text:
            return False

        cleaned = self.extract_clean_chinese_content(text)

        # Must have at least 2 Chinese characters to be meaningful
        chinese_char_count = len(re.findall(r'[\u4e00-\u9fff]', cleaned))
        return chinese_char_count >= 2

    def split_text_by_language(self, text: str) -> dict:
        """Split text into Chinese and non-Chinese parts"""
        if not text:
            return {'chinese': '', 'non_chinese': ''}

        cleaned = self.clean_text(text)

        # Extract Chinese characters
        chinese_chars = re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u3000-\u303f\uff00-\uffef]', cleaned)
        chinese_text = ''.join(chinese_chars)

        # Extract non-Chinese characters
        non_chinese_chars = re.findall(r'[^\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u3000-\u303f\uff00-\uffef]', cleaned)
        non_chinese_text = ''.join(non_chinese_chars)

        return {
            'chinese': chinese_text.strip(),
            'non_chinese': non_chinese_text.strip()
        }