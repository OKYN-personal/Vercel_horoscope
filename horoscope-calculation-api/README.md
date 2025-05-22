# ホロスコープ計算API

このリポジトリは、ホロスコープ計算アプリケーションのバックエンドAPI部分です。

## 特徴

- SwissEphを使用した天文計算
- 軽量化のためのメモリキャッシュ
- コールドスタート最適化

## デプロイ方法

### Render.comへのデプロイ

1. Render.comでアカウント作成
   - https://render.com/ にアクセス

2. 新しいウェブサービスを作成
   - 「New +」→「Web Service」
   - GitHubリポジトリを接続

3. 設定
   - **Name**: horoscope-calculation-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python download_ephe.py`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free

4. 環境変数の設定
   - **PYTHONUNBUFFERED**: 1
   - **EPHEPATH**: /var/data/ephe

5. デプロイを実行
   - 「Create Web Service」ボタンをクリック

## ローカルでの開発

```bash
# 依存関係のインストール
pip install -r requirements.txt

# エフェメリスファイルのダウンロード
python download_ephe.py

# 開発サーバーの起動
python app.py
```

## APIエンドポイント

- `POST /calculate`: ホロスコープ計算
  - リクエスト: `{"birth_date": "YYYY-MM-DD", "birth_time": "HH:MM", "latitude": 35.6895, "longitude": 139.6917}`
  - レスポンス: 天体位置とハウス情報

- `GET /warmup`: サーバーのウォームアップ
  - レスポンス: `{"status": "warmed up"}`

- `GET /health`: ヘルスチェック
  - レスポンス: `{"status": "ok", "service": "calculation-api", "cache_size": 0}`

## ファイル構造

- `app.py`: メインアプリケーション
- `download_ephe.py`: エフェメリスファイルダウンロードスクリプト
- `render.yaml`: Renderデプロイ設定
- `Dockerfile`: Dockerコンテナ設定
- `requirements.txt`: Python依存関係

## 使用技術

- Flask: ウェブフレームワーク
- SwissEph: 天文計算ライブラリ
- gunicorn: 本番用WSGIサーバー 