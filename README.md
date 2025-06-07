# 🎬 AI AA Slideshow Maker

AIが入力されたテキストを2人の登場人物（AさんとBさん）による会話形式のシナリオに変換し、各セリフに対応するアスキーアート（AA）を生成して、音声付きスライドショーを作成するWebアプリケーションです。

## ✨ 主な機能

- **テキスト→会話変換**: Google Gemini AIが入力テキストを自然な会話形式に変換
- **AA生成**: AIが各セリフに適したアスキーアート（AA）を自動生成
- **音声付きスライドショー**: Web Speech APIによる日本語音声読み上げ
- **美しいUI**: モダンで使いやすいWebインターフェース
- **Docker対応**: 簡単なセットアップと環境構築
- **複数AAスタイル**: ゆっくり、2ch、デフォルトなど複数のAAスタイルに対応

## 🛠 技術スタック

- **コンテナ**: Docker, Docker Compose
- **バックエンド**: Python 3.11, Flask
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+)
- **AI API**: Google Gemini API (gemini-1.5-flash) - 会話生成とAA生成
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
    │   ├── aa_generation_default.md       # デフォルトAA生成用プロンプト
    │   ├── aa_generation_yukkuri.md       # ゆっくりAA生成用プロンプト
    │   └── aa_generation_2ch.md           # 2chAA生成用プロンプト
    └── templates/
        └── index.html      # フロントエンドUI
```

## 🚀 セットアップ手順

### 前提条件

以下がインストールされていることを確認してください：

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. APIキーの取得

このアプリケーションを使用するには、Google Gemini APIキーが必要です：

#### Google Gemini API（必須）
1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
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
```

**注意**: `your_actual_gemini_api_key_here` の部分を、取得した実際のGemini APIキーに置き換えてください。

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
2. **AAスタイル選択**: お好みのAAスタイル（デフォルト、ゆっくり、2ch）を選択
3. **生成開始**: 「スライドショーを生成」ボタンをクリック
4. **AI処理**: AIが会話形式のシナリオと対応AAを生成（数分かかる場合があります）
5. **スライドショー再生**: 自動的に音声付きAAスライドショーが再生されます

## 🎨 AAスタイルについて

- **default**: 基本的なアスキーアート
- **yukkuri**: ゆっくり系のキャラクター表現
- **2ch**: 2ちゃんねる風のAA表現

各スタイルは専用のプロンプトで最適化されており、異なる表現スタイルのAAを楽しめます。

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
- **`aa_generation_*.md`**: 各スタイルのAA生成用プロンプト

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

3. **AA生成の失敗**
   - Gemini APIの利用制限に達していないか確認
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

**楽しいAAスライドショー作成をお楽しみください！** 🎉 