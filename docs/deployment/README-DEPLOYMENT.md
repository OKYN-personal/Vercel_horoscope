# ホロスコープアプリケーション マイクロサービスデプロイ戦略

## アーキテクチャの改善

Vercelのサーバーレス関数250MB制限の問題を解決するため、マイクロサービスアーキテクチャに移行します。

## 1. マイクロサービスアーキテクチャ

### コンポーネント

1. **フロントエンドプロキシ**
   - Vercelにデプロイ
   - 静的ファイル提供とAPIリクエストのプロキシ
   - 最小限の依存関係とコード

2. **計算APIサーバー**
   - Google Cloud Run または AWS ECS/App Runner
   - ホロスコープ計算ロジック
   - エフェメリスファイルを含む
   - Docker化済み

## 2. フロントエンドプロキシ (Vercel)

### 構成要素
- `api/index.py`: リクエストを計算APIに転送
- `static/`: HTML, CSS, JavaScriptファイル
- 依存関係: Flask, requests（最小限）

### デプロイ手順
1. Vercelにログイン
2. リポジトリを連携
3. 環境変数`CALCULATION_API`に計算APIのURLを設定
4. デプロイ

## 3. 計算APIサーバー (Google Cloud Run)

### 構成要素
- `app.py`: ホロスコープ計算APIエンドポイント
- 依存関係: Flask, swisseph, flask-cors
- エフェメリスファイル: ビルド時またはコンテナ起動時にダウンロード

### デプロイ手順
1. Dockerイメージのビルド
   ```
   docker build -t horoscope-calculation-api .
   ```

2. Google Container Registryにプッシュ
   ```
   docker tag horoscope-calculation-api gcr.io/[PROJECT_ID]/horoscope-calculation-api
   docker push gcr.io/[PROJECT_ID]/horoscope-calculation-api
   ```

3. Cloud Runにデプロイ
   ```
   gcloud run deploy horoscope-calculation-api \
     --image gcr.io/[PROJECT_ID]/horoscope-calculation-api \
     --platform managed \
     --region [REGION] \
     --allow-unauthenticated
   ```

## 4. AWS App Runner代替手順（必要に応じて）

1. ECRリポジトリ作成
   ```
   aws ecr create-repository --repository-name horoscope-calculation-api
   ```

2. イメージのタグ付けとプッシュ
   ```
   aws ecr get-login-password | docker login --username AWS --password-stdin [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com
   docker tag horoscope-calculation-api [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/horoscope-calculation-api
   docker push [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/horoscope-calculation-api
   ```

3. App Runnerサービス作成（AWSコンソールから）

## 5. ローカル開発・テスト

1. 計算APIのローカル実行
   ```
   cd calculation_api
   pip install -r requirements.txt
   python app.py
   ```

2. フロントエンドプロキシのローカル実行
   ```
   cd ..
   pip install -r requirements.txt
   export CALCULATION_API=http://localhost:8080
   python api/index.py
   ```

## 6. 将来の拡張計画

1. CDN経由でのエフェメリスファイル配布
2. キャッシュレイヤの追加
3. データベースを使用した計算結果の保存
4. ユーザー認証の実装 