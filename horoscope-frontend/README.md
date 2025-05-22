# ホロスコープアプリ - フロントエンド

このリポジトリは、ホロスコープ計算アプリケーションのフロントエンド部分です。

## 特徴

- 軽量な静的フロントエンド
- Vercelで無料デプロイ可能
- 外部APIと通信して計算処理を行う
- PWA（Progressive Web App）対応
  - オフラインモード対応
  - ホーム画面にインストール可能
  - モバイル最適化UI

## デプロイ方法

### Vercelへのデプロイ

1. Vercelでアカウント作成
   - https://vercel.com/ にアクセス

2. 新しいプロジェクトをインポート
   - 「Add New...」→「Project」

3. 設定
   - **Framework Preset**: Other
   - **Root Directory**: /（ルートディレクトリ）
   - **Build Command**: `mkdir -p static/css static/js && cp -r static/* .vercel/output/static/`

4. 環境変数の設定
   - **PYTHONPATH**: .
   - **CALCULATION_API**: 計算API用サーバーのURL

5. デプロイを実行
   - 「Deploy」ボタンをクリック

## ローカルでの開発

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 開発サーバーの起動
python api/index.py
```

ブラウザで http://localhost:5000 にアクセスすると、アプリケーションが表示されます。

## ファイル構造

- `api/`: Flask APIプロキシ
- `static/`: 静的ファイル（HTML, CSS, JavaScript）
- `vercel.json`: Vercelデプロイ設定
- `requirements.txt`: Python依存関係

## 使用技術

- Flask: APIプロキシ
- JavaScript: クライアントサイドのロジック
- HTML/CSS: ユーザーインターフェース
- Service Worker: PWA機能（キャッシュとオフライン対応）
- Geolocation API: 位置情報取得

## PWA機能

このアプリケーションは以下のPWA機能を実装しています：

1. **オフライン対応**
   - 静的ファイルのキャッシュによるオフライン表示
   - 過去の計算結果のローカルストレージ保存

2. **インストール可能**
   - ホーム画面にインストール可能
   - スタンドアロンモードで動作

3. **モバイル最適化**
   - レスポンシブデザイン
   - タッチ操作の最適化
   - 位置情報を利用した現在地の取得 