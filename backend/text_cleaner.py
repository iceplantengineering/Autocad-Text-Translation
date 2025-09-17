import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self):
        # DXF/MTEXT format codes to remove
        self.format_patterns = [
            # MTEXT formatting codes
            r'\\pi-?\d+,-?\d+;',      # Paragraph indentation
            r'\\pi-?\d+;',            # Paragraph indentation (simplified)
            r'\\P',                   # Paragraph break
            r'\\p\d+;',               # Paragraph formatting
            r'\\l\d+;',               # Line spacing
            r'\\f[^;]+;',             # Font specification
            r'\\[HOQTL]+;?',          # Justification codes
            r'\\[cC]\d+;',            # Color specification
            r'\\[hH]\d+\.?\d*;',     # Text height
            r'\\[wW]\d+\.?\d*;',     # Width factor
            r'\\[aA]\d+;',            # Alignment angle
            r'\\[qQ]\d+;',            # Oblique angle
            r'\\[Ss](?:.*?);',       # Stacking text
            r'\\[{}]',                # Braces
            r'\{.*?\}',               # Content in braces
            r'\\[A-Za-z]\d*;',       # Other format codes
            r'\{\\[^}]+\}',          # Format codes in braces
        ]

        # Special characters to clean
        self.special_chars = [
            (r'[\x00-\x1f\x7f-\x9f]', ''),  # Control characters
            (r'\s+', ' '),                   # Multiple spaces to single space
            (r'^\s+|\s+$', ''),             # Leading/trailing spaces
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

        # Remove DXF formatting codes
        for pattern in self.format_regex:
            cleaned_text = pattern.sub('', cleaned_text)

        # Clean special characters
        for pattern, replacement in self.special_regex:
            cleaned_text = pattern.sub(replacement, cleaned_text)

        # Remove extra whitespace
        cleaned_text = ' '.join(cleaned_text.split())

        logger.debug(f"Text cleaning: '{original_text}' -> '{cleaned_text}'")
        return cleaned_text.strip()

    def clean_chinese_text(self, text: str) -> str:
        """Clean Chinese text specifically, preserving meaningful content"""
        if not text:
            return text

        cleaned = self.clean_text(text)

        # Additional cleaning for Chinese text
        cleaned = re.sub(r'[，,、。；：！？""''（）【】《》〈〉…—]+', ' ', cleaned)  # Chinese punctuation to space
        cleaned = re.sub(r'[a-zA-Z0-9\s]+[\u4e00-\u9fff]', lambda m: m.group(), cleaned)  # Keep mixed content

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