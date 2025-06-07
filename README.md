# 🎬 AI Slideshow Maker

AIが入力されたテキストを2人の登場人物（AさんとBさん）による会話形式のシナリオに変換し、各セリフに対応する画像を生成して、音声付きスライドショーを作成するWebアプリケーションです。

## ✨ 主な機能

- **テキスト→会話変換**: Google Gemini AIが入力テキストを自然な会話形式に変換
- **AI画像生成**: Leonardo.Ai APIが各セリフに適した画像を自動生成
- **音声付きスライドショー**: Web Speech APIによる日本語音声読み上げ
- **美しいUI**: モダンで使いやすいWebインターフェース
- **Docker対応**: 簡単なセットアップと環境構築

## 🛠 技術スタック

- **コンテナ**: Docker, Docker Compose
- **バックエンド**: Python 3.11, Flask
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+)
- **AI API**: 
  - Google Gemini API (gemini-1.5-flash) - 会話生成
  - Leonardo.Ai API - 画像生成
- **ブラウザAPI**: Web Speech API - 音声合成

## 📁 プロジェクト構造

```
my-slideshow-app/
├── .gitignore
├── .env.example              # 環境変数テンプレート
├── .env                     # APIキー設定ファイル（要作成）
├── docker-compose.yml       # Docker構成
├── README.md               # このファイル
└── backend/
    ├── Dockerfile          # Flaskアプリ用Docker設定
    ├── requirements.txt    # Python依存関係
    ├── app.py             # メインアプリケーション
    ├── prompts/           # AIプロンプト管理
    │   ├── conversation_generation.md     # 会話生成用プロンプト
    │   ├── image_prompt_generation.md     # 画像プロンプト生成用
    │   └── aa_generation.md              # AA生成用プロンプト
    └── templates/
        └── index.html      # フロントエンドUI
```

## 🚀 セットアップ手順

### 前提条件

以下がインストールされていることを確認してください：

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. APIキーの取得

このアプリケーションを使用するには、以下のAPIキーが必要です：

#### Google Gemini API（必須）
1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. 生成されたAPIキーをコピー

#### Leonardo.Ai API（画像生成モード使用時のみ必要）
**注意**: モックモード（AA生成）のみを使用する場合は、このAPIキーは不要です。

1. [Leonardo.Ai](https://leonardo.ai/)でアカウント作成
2. ダッシュボードにログイン
3. API設定画面でAPIキーを生成
4. 生成されたAPIキーをコピー

### 2. 環境変数の設定

プロジェクトルートディレクトリで、環境変数ファイルを作成します：

```bash
# プロジェクトディレクトリに移動
cd my-slideshow-app

# .envファイルを作成
cp .env.example .env
```

**重要**: `.env`ファイルを作成し、以下の内容を記述してください：

```bash
# .env ファイルの内容
GEMINI_API_KEY=your_actual_gemini_api_key_here
# LEONARDO_API_KEY=your_actual_leonardo_api_key_here  # 画像生成モード使用時のみ必要
```

**注意**: 
- `your_actual_gemini_api_key_here` の部分を、取得した実際のGemini APIキーに置き換えてください。
- Leonardo.Ai APIキーは、モックモード（AA生成）のみを使用する場合は設定不要です。
- 画像生成モードも使用したい場合は、`#` を削除してLeonardo.Ai APIキーを設定してください。

### 3. アプリケーションの起動

```bash
# Dockerコンテナをビルドして起動
docker-compose up --build -d

# ログを確認（オプション）
docker-compose logs -f
```

### 4. アプリケーションにアクセス

ブラウザで以下のURLにアクセスしてください：

```
http://localhost:5001
```

## 📝 使用方法

1. **テキスト入力**: テキストエリアに物語や説明文を入力
2. **生成開始**: 「スライドショーを生成」ボタンをクリック
3. **AI処理**: AIが会話形式のシナリオと対応画像を生成（数分かかる場合があります）
4. **スライドショー再生**: 自動的に音声付きスライドショーが再生されます

## 🔧 開発・デバッグ

### ログの確認

```bash
# アプリケーションログを表示
docker-compose logs backend

# リアルタイムでログを監視
docker-compose logs -f backend
```

### アプリケーションの停止

```bash
# コンテナを停止
docker-compose down

# コンテナとボリュームを完全に削除
docker-compose down -v
```

### 開発モード

`backend`ディレクトリはボリュームマウントされているため、ソースコードを変更すると自動的にFlaskアプリが再読み込みされます。

### プロンプト管理

AIに送信するプロンプトは、`backend/prompts/`ディレクトリで管理されています：

- **`conversation_generation.md`**: テキストから会話形式への変換プロンプト
- **`image_prompt_generation.md`**: 日本語セリフから英語画像プロンプトへの変換
- **`aa_generation.md`**: セリフからアスキーアート生成用プロンプト

プロンプトを調整したい場合は、これらのMarkdownファイルを編集してからDockerコンテナを再起動してください：

```bash
# プロンプト修正後の再起動
docker-compose restart backend
```

## ⚠️ トラブルシューティング

### よくある問題と解決方法

1. **APIキーエラー**
   - `.env`ファイルが正しく作成されているか確認
   - APIキーが正確にコピーされているか確認
   - APIキーに有効期限がないか確認

2. **Docker関連エラー**
   - Dockerが起動しているか確認
   - ポート5001が他のアプリケーションで使用されていないか確認

3. **画像生成の失敗**
   - Leonardo.Ai APIの利用制限に達していないか確認
   - ネットワーク接続を確認

4. **音声が再生されない**
   - ブラウザが音声を許可しているか確認
   - ブラウザがWeb Speech APIに対応しているか確認

## 🤝 貢献

プロジェクトへの貢献を歓迎します！

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 📞 サポート

質問や問題がある場合は、GitHubのIssuesでお知らせください。

---

**楽しいスライドショー作成をお楽しみください！** 🎉 