# DWGファイル対応セットアップガイド

## 現在の状況
AutoCAD DWGファイルの中国語→日本語翻訳システムはほぼ完成していますが、DWGからDXFへの変換機能には外部ツールが必要です。

## 必要なツール
以下のいずれかのツールをインストールすることで、DWGファイルの直接処理が可能になります：

### オプション1: ODA File Converter（推奨）
[ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter)をダウンロードしてインストールしてください。

**インストール手順:**
1. 上記リンクからODA File Converterをダウンロード
2. インストールを実行（通常は `C:\Program Files\ODA\ODAFileConverter\` にインストール）
3. 自動的にシステムのパスに追加されます

### オプション2: AutoCAD
AutoCADがインストールされている場合、COM経由で自動的に変換できます。

### オプション3: LibreCAD
[LibreCAD](https://librecad.org/)をインストールすると、コマンドライン変換が可能になります。

## 現在利用可能な機能
- ✅ DXFファイルの完全なサポート
- ✅ 中国語テキスト抽出と翻訳
- ✅ テキスト置換とフォーマット保持
- ⏳ DWGファイル（変換ツールインストール後）

## 緊急対応策
DWG変換ツールをインストールできない場合：

1. **AutoCADで手動変換:**
   - DWGファイルをAutoCADで開く
   - 「名前を付けて保存」→DXF形式で保存
   - 生成されたDXFファイルをアップロード

2. **オンライン変換サービス:**
   - [AnyConv](https://anyconv.com/ja/dwg-to-dxf-converter/)
   - [Zamzar](https://www.zamzar.com/convert/dwg-to-dxf/)
   - などのオンラインサービスで変換

## テスト方法
1. このガイドに従って変換ツールをインストール
2. ブラウザで `http://localhost:3000` を開く
3. DWGファイルをアップロードしてテスト

## 技術詳細
システムは以下の変換方法を順に試行します：
1. ODA File Converter
2. Teigha File Converter
3. AutoCAD COMオートメーション
4. LibreCADコマンドライン
5. オンライン変換サービス（開発中）

## サポート情報
問題が発生した場合は、以下のデバッグエンドポイントで詳細情報を確認できます：
- `http://localhost:8002/debug/test-dwg-conversion/{filename}`
- `http://localhost:8002/debug/test-file/{filename}`

---
*このガイドはZAItryプロジェクト用に作成されました*