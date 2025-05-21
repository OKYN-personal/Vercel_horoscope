# ホロスコープPWAアプリ

占星術のホロスコープを計算し、サビアンシンボルの解釈を提供するウェブアプリケーションです。PWA（Progressive Web App）機能を備えており、スマートフォンやタブレットにインストールして利用できます。

## 主な機能

- ホロスコープ計算と天体配置の表示
- サビアンシンボルの解釈
- トランジット（現在の天体と出生図の関係）表示
- 相性占い（シナストリー）
- 月のノード計算
- ライフイベント予測
- PDF出力
- PWA機能（オフライン対応、ホーム画面インストール）
- プッシュ通知（天文イベント通知）

## 開発環境のセットアップ

### 前提条件

- Python 3.8以上
- pip
- Git

### インストール手順

1. リポジトリをクローン：
   ```
   git clone <repository-url>
   cd horoscope
   ```

2. 仮想環境を作成して有効化：
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. 依存ライブラリをインストール：
   ```
   pip install -r requirements.txt
   ```

4. アプリケーションを実行：
   ```
   python run.py
   ```

5. ブラウザで開く：
   ```
   http://localhost:5000
   ```

## スマホでPWAとして使用する方法

### ローカル開発環境でのテスト

1. パソコンのIPアドレスを確認（Windowsの場合）：
   ```
   ipconfig
   ```

2. スマホのブラウザで以下のURLにアクセス：
   ```
   http://<パソコンのIPアドレス>:5000
   ```
   ※パソコンとスマホは同じWi-Fiネットワークに接続する必要があります。

3. ホーム画面に追加：
   - iPhoneの場合：共有ボタン→「ホーム画面に追加」
   - Androidの場合：メニュー→「ホーム画面に追加」

### Vercelにデプロイする手順

1. GitHubリポジトリを作成し、コードをプッシュ：
   ```
   git remote add origin <github-repo-url>
   git push -u origin main
   ```

2. Vercelをインストール：
   ```
   npm install -g vercel
   ```

3. Vercelにログイン：
   ```
   vercel login
   ```

4. デプロイを実行：
   ```
   vercel
   ```
   - プロジェクト設定についての質問に答えます
   - スコープ、プロジェクト名、ディレクトリなどを選択します

5. デプロイが完了したら、提供されたURLでアプリにアクセスできます。

## プッシュ通知の設定

1. PWAテストページで「プッシュ通知を許可する」をクリック
2. 通知権限の許可ダイアログで「許可」を選択
3. 天文イベント通知を受け取る設定が完了します

## 天文イベント通知の自動実行

天文イベント通知を自動的に送信するには、サーバー上でcronジョブを設定します：

```
# 毎日午前9時に天文イベントをチェックして通知
0 9 * * * cd /path/to/horoscope && /path/to/python astronomical_events_notifier.py >> /path/to/logs/events.log 2>&1
```

## ライセンス

このプロジェクトは [ライセンス名] のもとで公開されています。詳細はLICENSEファイルを参照してください。

## 開発者

[開発者名や連絡先など] 