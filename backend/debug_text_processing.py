from debug_translation_service import DebugTranslationService
from text_cleaner import TextCleaner

def test_text_processing():
    """テキスト処理のデバッグ"""
    translation_service = DebugTranslationService()
    text_cleaner = TextCleaner()

    # 実際の図面から抽出された中国語テキスト
    test_texts = [
        "备 注",
        "合 计",
        "质 量 kg",
        "单 件",
        "材 料",
        "数量",
        "名 称 及 规 格",
        "序号",
        "图号、型号或标准号",
        "总   页,第   页",
        "工艺平面图",
        "塑料件涂装线",
        "货淋室",
        "快速卷帘门",
        "接地"
    ]

    print("=== テキスト処理デバッグ ===")

    # Set output encoding for UTF-8
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    for text in test_texts:
        print(f"\n--- テキスト: '{text}' ---")

        # クリーニング処理
        cleaned = text_cleaner.clean_chinese_text(text)
        extracted = text_cleaner.extract_clean_chinese_content(text)

        print(f"クリーニング済み: '{cleaned}'")
        print(f"抽出された中国語: '{extracted}'")

        # 中国語検出
        is_chinese = translation_service.detect_chinese_text(text)
        print(f"中国語検出: {is_chinese}")

        # 翻訳辞書の存在確認
        direct_match = text in translation_service.mock_translations
        cleaned_match = cleaned in translation_service.mock_translations
        extracted_match = extracted in translation_service.mock_translations

        print(f"直接一致: {direct_match}")
        print(f"クリーニング済み一致: {cleaned_match}")
        print(f"抽出された中国語一致: {extracted_match}")

        # スペース除去バージョンも確認
        no_space_text = text.replace(' ', '')
        no_space_cleaned = cleaned.replace(' ', '')
        no_space_extracted = extracted.replace(' ', '')

        no_space_match = no_space_text in translation_service.mock_translations
        no_space_cleaned_match = no_space_cleaned in translation_service.mock_translations
        no_space_extracted_match = no_space_extracted in translation_service.mock_translations

        print(f"スペース除去一致: {no_space_match}")
        print(f"スペース除去クリーニング一致: {no_space_cleaned_match}")
        print(f"スペース除去抽出一致: {no_space_extracted_match}")

        # 実際に翻訳を試みる
        import asyncio
        async def test_translate():
            result = await translation_service.translate([text])
            print(f"翻訳結果: '{result[0]['translated_text']}'")

        asyncio.run(test_translate())

if __name__ == "__main__":
    test_text_processing()