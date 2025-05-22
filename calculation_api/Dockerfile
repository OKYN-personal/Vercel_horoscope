FROM python:3.9-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# エフェメリスデータディレクトリ作成
RUN mkdir -p ephe

# 環境変数の設定
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV EPHEPATH=/app/ephe

# アプリケーションの起動
CMD ["python", "app.py"] 