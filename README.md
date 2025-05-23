# スターゲイザー占星術アプリケーション

このリポジトリは、占星術チャート作成と解釈を提供するウェブアプリケーション「スターゲイザー」のソースコードを含んでいます。

## 主な機能

- 出生図（ネイタルチャート）の作成と解釈
- サビアンシンボルの解説
- トランジット分析
- PDF出力機能
- レスポンシブデザイン
- PWA対応

## プロジェクト構成

- `app/` - アプリケーションのメインコード
  - `templates/` - HTMLテンプレート
  - `static/` - CSS, JavaScript, 画像ファイル
  - `utils/` - ユーティリティ関数
  - `data/` - アプリケーションデータ
- `docs/` - ドキュメント
  - `requirements/` - 各機能の要件定義書
  - `development/` - 開発手順書
  - `checklists/` - 開発チェックリスト
  - `deployment/` - デプロイメント関連ドキュメント
  - `misc/` - その他のドキュメント
- `tests/` - テストコード
- `samples/` - サンプルファイル（HTML, PDF出力例）
- `ephe/` - 天体位置計算用のエフェメリスデータ
- `api/` - APIエンドポイント
- `calculation_api/` - 計算API
- `static/` - 静的ファイル

## セットアップ

1. リポジトリをクローン：
   ```
   git clone https://github.com/your-username/horoscope.git
   cd horoscope
   ```

2. 仮想環境の作成と有効化：
   ```
   python -m venv venv
   source venv/bin/activate  # Linuxの場合
   venv\Scripts\activate     # Windowsの場合
   ```

3. 依存パッケージのインストール：
   ```
   pip install -r requirements.txt
   ```

4. アプリケーションの実行：
   ```
   python run.py
   ```

## 開発計画

以下の機能拡張が計画されています：

1. パーソナライズ機能
2. 専門的解析機能
3. 教育コンテンツ
4. テクニカル強化
5. 高度な予測機能
6. 高度なチャート表示

詳細は `docs/requirements/` ディレクトリ内の各要件定義書を参照してください。

## ライセンス

このプロジェクトは独自ライセンスの下で提供されています。詳細については、プロジェクト管理者にお問い合わせください。 