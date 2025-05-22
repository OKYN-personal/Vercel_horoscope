# ホロスコープアプリ - 無料デプロイガイド

このガイドでは、ホロスコープアプリケーションを完全無料でデプロイする方法を説明します。

## 全体アーキテクチャ

```
ユーザー --> Vercel (フロントエンド) --> Render.com (計算API)
```

## 1. 計算APIをRender.comにデプロイ（無料）

Render.comは月100時間の無料ウェブサービス枠を提供しています。

### 手順

1. Render.comでアカウント作成
   - https://render.com/ にアクセスし、無料アカウントを作成

2. 新しいウェブサービスを作成
   - 「New +」→「Web Service」を選択
   - GitHubリポジトリを接続または手動デプロイを選択

3. 設定
   - **Name**: horoscope-calculation-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python download_ephe.py`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free（$0/month）

4. 環境変数の設定
   - **PYTHONUNBUFFERED**: 1
   - **EPHEPATH**: /var/data/ephe

5. デプロイを実行
   - 「Create Web Service」ボタンをクリック

### 注意点

- 無料プランでは15分間アクセスがないとスリープ状態になります
- 初回アクセス時はウェイクアップに数秒かかります（コールドスタート）
- 月100時間の制限があるため、継続的なアクセスがある場合は注意が必要です

## 2. フロントエンドをVercelにデプロイ（無料）

Vercelの無料プランを使用します。

### 手順

1. Vercelでアカウント作成
   - https://vercel.com/ にアクセスし、無料アカウントを作成

2. 新しいプロジェクトをインポート
   - 「Add New...」→「Project」を選択
   - GitHubリポジトリを接続

3. 設定
   - **Framework Preset**: Other
   - **Root Directory**: /（ルートディレクトリ）
   - **Build Command**: `mkdir -p static/css static/js && cp -r static/* .vercel/output/static/`

4. 環境変数の設定
   - **PYTHONPATH**: .
   - **CALCULATION_API**: Render.comで作成したAPIのURL（例: https://horoscope-calculation-api.onrender.com）

5. デプロイを実行
   - 「Deploy」ボタンをクリック

## 3. 定期的なウォームアップ（オプション）

スリープを防ぐために、無料の定期実行サービスでAPIをウォームアップできます。

1. Cronitor, UptimeRobot, Heartbeatなどの無料サービスを使用
2. `https://your-api.onrender.com/warmup` に5分おきにリクエストを送信

## 問題解決

### スリープによる初回レスポンスの遅延

- ユーザーにローディング表示を十分に行う
- ページ読み込み時に自動的にウォームアップリクエストを送信

### 月間使用時間の制限

- 使用頻度が高くなった場合は、ユーザーごとの使用制限を設ける
- 一日あたりの計算回数を制限する

## 将来の拡張

1. 使用量が増えた場合は以下の有料プランを検討：
   - Render.com Standard ($7/月〜)
   - AWS Lambda（従量課金）
   - Google Cloud Run（従量課金）

2. キャッシュ機能の強化
   - 計算結果の永続化にFirebase Realtime Databaseなど無料サービスを活用 