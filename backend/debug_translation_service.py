import asyncio
import logging
from typing import List, Dict
from text_cleaner import TextCleaner

# ログ設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugTranslationService:
    """デバッグ用翻訳サービス"""

    def __init__(self):
        self.text_cleaner = TextCleaner()
        # より多くの中国語テキストを追加
        self.mock_translations = {
            # 基本的なCAD用語
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

            # 建築用語
            "平面图": "平面図",
            "立面图": "立面図",
            "剖面图": "断面図",
            "详图": "詳細図",
            "总平面图": "配置図",
            "结构图": "構造図",
            "施工图": "施工図",

            # 構造用語
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

            # テスト用の一般的な中国語
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

            # 追加のテスト用語
            "项目名称": "プロジェクト名",
            "图纸编号": "図面番号",
            "设计": "設計",
            "工程师": "エンジニア",
            "日期": "日付",
            "比例": "スケール",
            "单位": "単位",
            "长度": "長さ",
            "宽度": "幅",
            "高度": "高さ",
            "面积": "面積",
            "体积": "体積",

            # テストファイル内の実際のテキスト
            "图层: 建筑平面图": "レイヤー: 建築平面図",
            "块: 柱子": "ブロック: 柱",
            "标注: 1:100": "寸法: 1:100",
            "文字: 测试文本": "テキスト: テスト文章",
            "多行文字: 这是一个测试多行文本示例": "マルチテキスト: これはテスト用の複数行テキスト例です",
            "插入点: (0,0,0)": "挿入点: (0,0,0)",
            "旋转: 90度": "回転: 90度",
            "比例: 1:50": "スケール: 1:50",
            "线型: CONTINUOUS": "線種: CONTINUOUS",
            "颜色: RED": "色: 赤",
            "线宽: 0.5mm": "線幅: 0.5mm",
            "项目名称: 测试项目": "プロジェクト名: テストプロジェクト",
            "图纸编号: A-001": "図面番号: A-001",
            "设计: 工程师": "設計: エンジニア",
            "日期: 2024-01-01": "日付: 2024-01-01",
            "比例: 1:100": "スケール: 1:100",
            "单位: 毫米": "単位: ミリメートル",

            # 実際の図面で見つかった用語
            "备 注": "備考",
            "合 计": "合計",
            "质 量 kg": "質量 kg",
            "单 件": "単品",
            "材 料": "材料",
            "数量": "数量",
            "名 称 及 规 格": "名称及び仕様",
            "序号": "番号",
            "图号、型号或标准号": "図番、型式又は標準番号",
            "总   页,第   页": "総　頁,第　頁",
            "工艺平面图": "工程平面図",
            "塑料件涂装线": "プラスチック部品塗装ライン",
            "货淋室": "エアシャワールーム",
            "快速卷帘门": "高速巻きシャッター",
            "接地": "アース",
            "涂装线技术参数": "塗装ライン技術パラメータ",
            "工件名称": "ワーク名",
            "卡车保险杠": "トラックバンパー",
            "最大重量": "最大重量",
            "输送方式": "搬送方式",
            "工艺台车": "工程台車",
            "人工推拉": "手動押し引き",
            "涂装工艺流程": "塗装工程フロー",
            "上件": "ワークセット",
            "喷漆": "塗装",
            "油漆烘干": "塗装乾燥",
            "货淋室外购": "エアシャワールーム外注",
            "进出口": "出入口",
            "电动卷帘门": "電動巻きシャッター",
            "喷漆室": "塗装室",
            "干式纸盒": "ドライ式ボックス",
            "侧排风": "側面排気",
            "送风机组": "送風ユニット",
            "排风机组": "排風ユニット",
            "二层平台": "2階プラットフォーム",
            "室体": "ルーム本体",
            "镀锌板": "亜鉛メッキ板",
            "手动推拉门": "手動引き戸",
            "烘干": "乾燥",
            "柴油加热炉": "ディーゼル加熱炉",
            "燃烧器": "バーナー",
            "烘干温度": "乾燥温度",
            "烘干时间": "乾燥時間",
            "热风循环加热": "熱風循環加熱",
            "上送风下回风": "上送風下還風",
            "旋转门": "回転ドア",
            "人工开启": "手動開閉",
            "内腔高度": "内部高さ",
            "遮蔽工作台": "マスキング作業台",
            "工艺台车": "工程台車",
            "客户自备": "客先支給",
            "建议厂房内净空高度": "推奨建屋内クリアランス高さ",
            "卡车": "トラック",
            "保险杠": "バンパー",
            "塑料件": "プラスチック部品",
            "尺寸": "寸法",
            "重量": "重量",
            "喷漆台": "塗装台",
            "台车": "台車",
            "烘干室": "乾燥室",
            "钢平台": "鋼製プラットフォーム",
            "时间": "時間",
            "进出口": "出入口",
            "厂家": "メーカー",
            "按图制作": "図面通り製作",
            "结构": "構造",
            "布置": "配置",
            "机组": "ユニット",
            "室体": "ルーム本体",
            "燃烧器": "バーナー",
            "顶部": "天井",
            "温度": "温度",
            "热风": "熱風",
            "循环": "循環",
            "加热": "加熱",
            "送风": "送風",
            "回风": "還風",
            "开启": "開閉",
            "控制": "制御",
            "左右": "左右",
            "工作台": "作業台",
            "自备": "自前準備",
            "建议": "推奨",
            "厂房": "建屋",
            "内": "内部",
            "净空": "クリアランス",
            "高度": "高さ",

            # 具体的技术术语（完整短语）
            "长2000X宽500X高600mm": "長2000X幅500X高600mm",
            "最大重量 5kg/只": "最大重量5kg/個",
            "烘干时间45min/车": "乾燥時間45分/台車",
            "烘干温度80℃": "乾燥温度80℃",
            "建议厂房内净空高度6.5m": "推奨建屋内クリアランス高さ6.5m",
            "卡车保险杠等塑料件": "トラックバンパー等プラスチック部品",
            "工艺台车运输": "工程台車搬送",
            "人工推拉": "手動押し引き",
            "单个保险杠放在喷漆室内设喷漆台进行喷涂": "個別バンパーを塗装室内の塗装台に設置して塗装実施",
            "油漆烘干": "塗装乾燥",
            "货淋室外购": "シャワーブース外注",
            "建议厂家按图制作": "メーカーに図面通り製作を依頼",
            "进出口采用电动卷帘门": "出入口に電動シャッター扉を採用",
            "喷漆室采用干式纸盒": "塗装室にドライ式ペーパーボックスを採用",
            "侧排风结构": "側面排風構造",
            "送风机组": "送風ユニット",
            "排风机组均布置在二层平台上": "排風ユニットを2階プラットフォームに配置",
            "室体采用镀锌板结构": "ルーム本体に亜鉛メッキ鋼板構造を採用",
            "采用手动推拉门": "手動スライド扉を採用",
            "烘干采用柴油加热炉": "乾燥にディーゼル加熱炉を採用",
            "燃烧器放在烘干室顶部二层钢平台上": "バーナーを乾燥室天井の2階鋼製プラットフォームに設置",
            "热风循环加热": "熱風循環加熱",
            "上送风下回风": "上側送風、下側還風",
            "进出口采用旋转门": "出入口に回転扉を採用",
            "人工开启": "手動開閉",
            "烘干室内腔高度控制在2m左右": "乾燥室内部高さを2m前後に制御",
            "遮蔽工作台": "マスキング作業台",
            "工艺台车客户自备": "工程台車は客先支給"
        }

    def detect_chinese_text(self, text: str) -> bool:
        """中国語テキストを検出"""
        if not text:
            return False

        # Clean text first to remove formatting codes
        cleaned_text = self.text_cleaner.clean_text(text)

        # Unicodeの中国語文字範囲をチェック
        chinese_ranges = [
            (0x4E00, 0x9FFF),    # CJK統漢字
            (0x3400, 0x4DBF),    # CJK統漢字拡張A
            (0x20000, 0x2A6DF),  # CJK統漢字拡張B
            (0xF900, 0xFAFF),    # 互換漢字
        ]

        chinese_chars = []
        for char in cleaned_text:
            code = ord(char)
            for start, end in chinese_ranges:
                if start <= code <= end:
                    chinese_chars.append(char)
                    break

        # Check if we have meaningful Chinese content
        has_chinese = len(chinese_chars) > 0 and self.text_cleaner.is_meaningful_chinese_text(cleaned_text)

        logger.debug(f"Text: '{text}' -> Cleaned: '{cleaned_text}' - Chinese chars: {chinese_chars} - Has Chinese: {has_chinese}")
        return has_chinese

    async def translate(self, texts: List[str], glossary: Dict[str, str] = None) -> List[Dict]:
        """翻訳を実行（デバッグ版）"""
        logger.info(f"Translating {len(texts)} texts")
        results = []

        for i, text in enumerate(texts):
            logger.debug(f"Processing text {i+1}: '{text}'")

            # テキストをクリーニング（フォーマットコードを除去）
            cleaned_text = self.text_cleaner.clean_chinese_text(text)
            extracted_chinese = self.text_cleaner.extract_clean_chinese_content(text)

            logger.debug(f"Original: '{text}' -> Cleaned: '{cleaned_text}' -> Extracted: '{extracted_chinese}'")

            # 直接翻訳辞書を探す
            translated_text = None

            # 完全一致を探す（元のテキスト、クリーニング済み、抽出された中国語、正規化されたテキストの順）
            normalized_texts = [
                text,
                cleaned_text,
                extracted_chinese,
                # スペースを除去したバージョンも試す
                text.replace(' ', ''),
                cleaned_text.replace(' ', ''),
                extracted_chinese.replace(' ', ''),
                # スペースを正規化したバージョン（全角スペースを半角に、複数スペースを1つに）
                ' '.join(text.split()),
                ' '.join(cleaned_text.split()),
                ' '.join(extracted_chinese.split())
            ]

            # デバッグ情報：検索対象テキストを表示
            logger.debug(f"Searching for matches among: {normalized_texts}")

            for source_text in normalized_texts:
                if source_text and source_text in self.mock_translations:
                    translated_text = self.mock_translations[source_text]
                    logger.debug(f"Found exact match for '{source_text}' -> '{translated_text}'")
                    break

            if not translated_text:
                # 部分一致を探す
                for key, value in self.mock_translations.items():
                    # クリーニング済みテキスト内でキーを探す
                    if key in cleaned_text:
                        # テキスト内の中国語部分を置換
                        translated_text = cleaned_text.replace(key, value)
                        logger.debug(f"Found partial match: '{key}' -> '{value}' in '{cleaned_text}'")
                        break

                if not translated_text:
                    # スペースを除去したバージョンでも部分一致を探す
                    cleaned_no_space = cleaned_text.replace(' ', '')
                    for key, value in self.mock_translations.items():
                        key_no_space = key.replace(' ', '')
                        if key_no_space in cleaned_no_space:
                            # スペースを除去した状態で置換
                            translated_text = cleaned_text.replace(key, value)
                            logger.debug(f"Found partial match (no space): '{key}' -> '{value}' in '{cleaned_text}'")
                            break

                if not translated_text and extracted_chinese:
                    # 抽出された中国語テキストで部分一致を探す
                    for key, value in self.mock_translations.items():
                        if key in extracted_chinese:
                            # クリーニング済みテキスト内の中国語部分を置換
                            translated_text = cleaned_text.replace(key, value)
                            logger.debug(f"Found partial match with extracted: '{key}' -> '{value}'")
                            break

                if not translated_text:
                    # 最終手段: 各文字を個別に翻訳
                    translated_parts = []
                    for char in cleaned_text:
                        if char in self.mock_translations:
                            translated_parts.append(self.mock_translations[char])
                        else:
                            translated_parts.append(char)
                    translated_text = ''.join(translated_parts)
                    logger.debug(f"Character-by-character translation: '{cleaned_text}' -> '{translated_text}'")

            # それでも見つからない場合
            if not translated_text or translated_text == cleaned_text:
                # デバッグ：辞書のキーを表示してマッチしない理由を調査
                logger.debug(f"Available dict keys containing Chinese: {[k for k in self.mock_translations.keys() if any(ord(c) >= 0x4E00 and ord(c) <= 0x9FFF for c in k)]}")
                translated_text = f"[翻訳済み: {extracted_chinese or cleaned_text}]"
                logger.debug(f"No translation found, using fallback: '{translated_text}'")

            # 少しディレイを追加（実際のAPI呼び出しをシミュレート）
            await asyncio.sleep(0.1)

            result = {
                "source_text": text,  # 元のテキストを保持
                "cleaned_text": cleaned_text,
                "extracted_chinese": extracted_chinese,
                "translated_text": translated_text,
                "source_lang": "ZH",
                "target_lang": "JA",
                "confidence": 0.95
            }

            results.append(result)
            logger.info(f"Translation {i+1}: '{text}' -> '{translated_text}'")

        logger.info(f"Completed translation of {len(texts)} texts")
        return results

    def filter_chinese_texts(self, text_entities: List[str]) -> List[str]:
        """中国語テキストをフィルタリング"""
        logger.info(f"Filtering {len(text_entities)} text entities for Chinese content")

        chinese_texts = []
        for text in text_entities:
            if self.detect_chinese_text(text):
                chinese_texts.append(text)
                extracted = self.text_cleaner.extract_clean_chinese_content(text)
                logger.debug(f"Chinese text found: '{text}' -> Extracted: '{extracted}'")
            else:
                logger.debug(f"Non-Chinese text skipped: '{text}'")

        logger.info(f"Found {len(chinese_texts)} Chinese texts out of {len(text_entities)} total")
        return chinese_texts

    def create_technical_glossary(self) -> Dict[str, str]:
        """技術用語の専門辞書を作成"""
        logger.info("Creating technical glossary")
        return self.mock_translations

    def print_all_translations(self):
        """すべての翻訳マッピングを表示"""
        print("=== 翻訳マッピング ===")
        for chinese, japanese in self.mock_translations.items():
            print(f"'{chinese}' -> '{japanese}'")
        print("==================")