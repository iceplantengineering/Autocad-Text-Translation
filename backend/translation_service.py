import os
import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float = 0.0
    alternative_translations: List[str] = None

class TranslationService:
    def __init__(self):
        self.deepl_api_key = os.getenv('DEEPL_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
        self.source_lang = 'ZH'  # Chinese
        self.target_lang = 'JA'  # Japanese

    async def translate_deepl(self, texts: List[str]) -> List[TranslationResult]:
        """Translate text using DeepL API"""
        if not self.deepl_api_key:
            raise ValueError("DeepL API key not configured")

        url = "https://api-free.deepl.com/v2/translate"
        headers = {"Authorization": f"DeepL-Auth-Key {self.deepl_api_key}"}

        results = []

        # DeepL supports batch translation up to 50 texts
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            data = {
                "text": batch,
                "source_lang": self.source_lang,
                "target_lang": self.target_lang
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=data) as response:
                        if response.status == 200:
                            translations = await response.json()
                            for trans in translations['translations']:
                                results.append(TranslationResult(
                                    source_text=trans.get('text', ''),
                                    translated_text=trans.get('detected_source_language', ''),
                                    source_lang=self.source_lang,
                                    target_lang=self.target_lang,
                                    confidence=1.0
                                ))
                        else:
                            error_text = await response.text()
                            logger.error(f"DeepL API error: {response.status} - {error_text}")
                            raise Exception(f"DeepL API error: {response.status}")

            except Exception as e:
                logger.error(f"DeepL translation failed: {str(e)}")
                raise

        return results

    async def translate_google(self, texts: List[str]) -> List[TranslationResult]:
        """Translate text using Google Cloud Translation API"""
        if not self.google_api_key:
            raise ValueError("Google Translate API key not configured")

        url = f"https://translation.googleapis.com/language/translate/v2?key={self.google_api_key}"
        headers = {"Content-Type": "application/json"}

        results = []

        # Google Translate supports batch translation
        batch_size = 100  # API limit
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            data = {
                "q": batch,
                "source": self.source_lang.lower(),
                "target": self.target_lang.lower(),
                "format": "text"
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            translations = await response.json()
                            for trans in translations['data']['translations']:
                                results.append(TranslationResult(
                                    source_text=trans.get('originalText', ''),
                                    translated_text=trans['translatedText'],
                                    source_lang=self.source_lang,
                                    target_lang=self.target_lang,
                                    confidence=1.0
                                ))
                        else:
                            error_text = await response.text()
                            logger.error(f"Google Translate API error: {response.status} - {error_text}")
                            raise Exception(f"Google Translate API error: {response.status}")

            except Exception as e:
                logger.error(f"Google translation failed: {str(e)}")
                raise

        return results

    async def translate_with_glossary(self, texts: List[str], glossary: Dict[str, str]) -> List[TranslationResult]:
        """Translate text with custom glossary terms"""
        # Pre-process texts with glossary replacements
        processed_texts = []
        temp_replacements = {}

        for i, text in enumerate(texts):
            processed_text = text
            # Replace glossary terms with temporary placeholders
            for source_term, target_term in glossary.items():
                placeholder = f"__GLOSSARY_{i}_{len(temp_replacements)}__"
                processed_text = processed_text.replace(source_term, placeholder)
                temp_replacements[placeholder] = target_term
            processed_texts.append(processed_text)

        # Translate the processed texts
        translated_results = await self.translate(processed_texts)

        # Post-process to replace placeholders with actual translations
        final_results = []
        for result in translated_results:
            final_text = result.translated_text
            # Replace placeholders with glossary terms
            for placeholder, target_term in temp_replacements.items():
                final_text = final_text.replace(placeholder, target_term)

            result.translated_text = final_text
            final_results.append(result)

        return final_results

    async def translate(self, texts: List[str], glossary: Optional[Dict[str, str]] = None) -> List[TranslationResult]:
        """Main translation method with fallback between services"""
        if glossary:
            return await self.translate_with_glossary(texts, glossary)

        # Try DeepL first if available
        if self.deepl_api_key:
            try:
                return await self.translate_deepl(texts)
            except Exception as e:
                logger.warning(f"DeepL translation failed, trying Google: {str(e)}")

        # Fallback to Google Translate
        if self.google_api_key:
            try:
                return await self.translate_google(texts)
            except Exception as e:
                logger.error(f"Google translation failed: {str(e)}")
                raise

        raise ValueError("No translation service available")

    def detect_chinese_text(self, text: str) -> bool:
        """Detect if text contains Chinese characters"""
        # Check for Chinese characters (Unicode ranges)
        chinese_ranges = [
            (0x4E00, 0x9FFF),    # Common Chinese
            (0x3400, 0x4DBF),    # Extension A
            (0x20000, 0x2A6DF),  # Extension B
            (0x2A700, 0x2B73F), # Extension C
            (0x2B740, 0x2B81F), # Extension D
            (0x2B820, 0x2CEAF), # Extension E
            (0xF900, 0xFAFF),    # Compatibility
        ]

        for char in text:
            code = ord(char)
            for start, end in chinese_ranges:
                if start <= code <= end:
                    return True
        return False

    def filter_chinese_texts(self, text_entities: List[str]) -> List[str]:
        """Filter and return only texts containing Chinese characters"""
        return [text for text in text_entities if self.detect_chinese_text(text)]

    def create_technical_glossary(self) -> Dict[str, str]:
        """Create a basic technical glossary for CAD/AEC terms"""
        return {
            # Common CAD terms
            "图层": "レイヤー",
            "块": "ブロック",
            "属性": "属性",
            "标注": "寸法",
            "文字": "テキスト",
            "多行文字": "マルチテキスト",
            "插入点": "挿入点",
            "旋转": "回転",
            "比例": "スケール",
            "线型": "線種",
            "颜色": "色",
            "线宽": "線幅",

            # Common architectural terms
            "平面图": "平面図",
            "立面图": "立面図",
            "剖面图": "断面図",
            "详图": "詳細図",
            "总平面图": "配置図",
            "结构图": "構造図",
            "施工图": "施工図",

            # Common engineering terms
            "混凝土": "コンクリート",
            "钢筋": "鉄筋",
            "钢结构": "鉄骨構造",
            "基础": "基礎",
            "柱": "柱",
            "梁": "梁",
            "板": "スラブ",
            "墙": "壁",
            "门": "ドア",
            "窗": "窓",
        }

    async def get_translation_cost_estimate(self, text_count: int, avg_chars_per_text: int = 50) -> Dict[str, float]:
        """Get cost estimate for translation"""
        total_chars = text_count * avg_chars_per_text

        # DeepL pricing (as of 2024)
        deepl_cost_per_char = 0.00002  # $0.00002 per character for API
        deepl_total = total_chars * deepl_cost_per_char

        # Google Translate pricing (as of 2024)
        google_cost_per_char = 0.00002  # $0.00002 per character
        google_total = total_chars * google_cost_per_char

        return {
            "deepl_cost": deepl_total,
            "google_cost": google_total,
            "total_chars": total_chars,
            "text_count": text_count
        }