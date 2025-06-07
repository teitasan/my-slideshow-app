# backend/Dockerfile

# 軽量で安定したPython 3.11の公式イメージをベースにする
FROM python:3.11-slim

# コンテナ内での作業ディレクトリを設定
WORKDIR /app

# パッケージインストールの前に、requirements.txtをコピーしてキャッシュを有効活用
COPY requirements.txt .

# 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコンテナにコピー
COPY . .

# コンテナ起動時にFlaskアプリケーションを実行するコマンド
# --host=0.0.0.0 を指定することで、コンテナの外部からアクセス可能にする
CMD ["flask", "run", "--host=0.0.0.0"] 