import asyncio
import random
from typing import List, Dict
from datetime import datetime

class MockTranslationService:
    """Mock translation service for testing without API keys"""

    def __init__(self):
        self.mock_translations = {
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

            # Generic Chinese text for testing
            "测试": "テスト",
            "你好": "こんにちは",
            "中国": "中国",
            "日本": "日本",
            "翻译": "翻訳",
            "项目": "プロジェクト",
            "设计": "設計",
            "图纸": "図面",
            "建筑": "建築",
            "结构": "構造",
            "机械": "機械",
            "电气": "電気",
            "给排水": "給排水",
            "暖通": "暖房換気",
        }

    def detect_chinese_text(self, text: str) -> bool:
        """Simple Chinese text detection"""
        chinese_chars = [char for char in text if '\u4e00' <= char <= '\u9fff']
        return len(chinese_chars) > 0

    async def translate(self, texts: List[str], glossary: Dict[str, str] = None) -> List[Dict]:
        """Mock translation - returns predefined translations"""
        results = []

        for text in texts:
            translated_text = self.mock_translations.get(text, f"[翻訳: {text}]")

            # Simulate processing delay
            await asyncio.sleep(0.1)

            results.append({
                "source_text": text,
                "translated_text": translated_text,
                "source_lang": "ZH",
                "target_lang": "JA",
                "confidence": 0.95
            })

        return results

    def filter_chinese_texts(self, text_entities: List[str]) -> List[str]:
        """Filter and return only texts containing Chinese characters"""
        return [text for text in text_entities if self.detect_chinese_text(text)]

    def create_technical_glossary(self) -> Dict[str, str]:
        """Create a technical glossary for CAD/AEC terms"""
        return self.mock_translations