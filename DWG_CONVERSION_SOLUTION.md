# DWG変換エラーの解決策

## 🚨 エラーの原因
"No DWG to DXF conversion method available" は、DWGファイルをDXFファイルに変換するためのツールがシステムにインストールされていないことが原因です。

## ✅ 即時解決策 - DXFファイルでテスト

### ステップ1: DXFファイルでテスト
アプリケーションはすでにDXFファイルをサポートしています。すぐにテストできます：

1. **テスト用DXFファイルを使用**
   - `test_files/test_chinese_text.dxf` を使用
   - このファイルには中国語テキストが含まれています

2. **ファイルアップロード**
   - http://localhost:3000 を開く
   - 「DWG/DXFファイルを選択」からDXFファイルを選択
   - アップロードして翻訳をテスト

### ステップ2: AutoCADでDXFを作成
AutoCADをお持ちの場合：
1. AutoCADで任意の図面を開く
2. 中国語テキストを追加
3. `SAVEAS` コマンドでDXF形式で保存

## 🔧 DWG変換を有効にする方法

### 方法1: ODA File Converter（推奨）
**無料で使えるDWG変換ツール**

1. **ダウンロード**
   - https://www.opendesign.com/guestfiles/oda_file_converter
   - "ODA File Converter" をダウンロード

2. **インストール**
   - インストーラーを実行
   - デフォルト設定でインストール

3. **パスを通す**
   - インストール先をシステムPATHに追加
   - 通常: `C:\Program Files\ODA\ODAFileConverter`

### 方法2: AutoCADを使用
AutoCADがインストールされている場合：

1. **AutoCADのCOMインターフェースを有効化**
   - AutoCADを管理者として実行
   - `OPTIONS` → 「システム」タブ
   - 「安全なモード」のチェックを外す

2. **Pythonライブラリのインストール**
```bash
pip install pywin32
```

### 方法3: LibreDWG（オープンソース）
```bash
# Linux/WSLの場合
sudo apt-get install libdwg-dev

# Pythonバインディング
pip install python-dwg
```

## 🧪 テスト手順

### 前提条件
- バックエンドサーバー起動: `python simple_app.py`
- フロントエンドサーバー起動: `python -m http.server 3000`

### テスト1: DXFファイルでのテスト
1. `test_files/test_chinese_text.dxf` を準備
2. http://localhost:3000 にアクセス
3. ファイルを選択してアップロード
4. 進捗を確認
5. 翻訳結果をダウンロード

### テスト2: DWGファイルでのテスト（変換ツールインストール後）
1. ODA File Converterをインストール
2. DWGファイルを準備
3. 同じ手順でテスト

## 📊 サポート状況

| ファイル形式 | 変換要件 | テスト状況 |
|---|---|---|
| DXF | 不要 | ✅ 動作確認済み |
| DWG | ODA File Converter または AutoCAD | ⚠️ 変換ツール必要 |
| DWF | 未対応 | ❌ |
| SVG | 未対応 | ❌ |

## 🔍 エラーメッセージの意味

| エラーメッセージ | 原因 | 解決策 |
|---|---|---|
| "No DWG to DXF conversion method available" | 変換ツール未インストール | ODA File Converterをインストール |
| "Failed to convert DWG to DXF" | 変換処理エラー | ファイルが破損しているか、バージョン非互換 |
| "Cannot find module 'win32com'" | pywin32未インストール | `pip install pywin32` |

## 🛠️ デバッグ方法

### ログの確認
バックエンドのコンソールに詳細なログが表示されます：
```
INFO: Converting DWG to DXF...
WARNING: ODA File Converter failed: [エラー詳細]
INFO: Successfully converted DWG to DXF using ODA File Converter
```

### テストファイルの確認
アップロードされたファイルは `backend/uploads/` に保存されます。

### 変換後のファイル確認
変換されたDXFファイルは一時ディレクトリに作成されます。

## 📝 開発者向け情報

### コードの変更点
- `simple_dwg_processor.py` を作成し、エラーハンドリングを改善
- DXFファイルのサポートを追加
- フロントエンドでDXFファイルを受け付けるように変更

### 変換処理の流れ
1. ファイル拡張子をチェック
2. DWGの場合は変換を実行
3. DXFファイルを処理
4. テキストを抽出
5. 翻訳を実行
6. テキストを置換
7. 結果を保存

## 🎯 次のステップ

1. ✅ **即時テスト**: DXFファイルでアプリケーションをテスト
2. 🔧 **変換ツールのインストール**: ODA File Converterをインストール
3. 🧪 **DWGテスト**: DWGファイルで完全なフローをテスト
4. 🚀 **本番デプロイ**: クラウド環境でのデプロイ準備

これでまずはDXFファイルでアプリケーションの全機能をテストできます！