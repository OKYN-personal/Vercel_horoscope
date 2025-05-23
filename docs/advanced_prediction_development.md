# 高度な予測機能 開発手順書

## 1. 開発準備

### 1.1 開発環境構築

1. **開発リポジトリのクローン**
   ```bash
   git clone https://github.com/yourusername/stargazer.git
   cd stargazer
   git checkout -b feature/advanced-predictions
   ```

2. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   # 追加で必要なパッケージ
   pip install pyswisseph pandas matplotlib
   ```

3. **Swiss Ephemerisのセットアップ**
   - Swiss Ephemerisデータファイルを`app/static/ephe/`にダウンロード配置
   - テストファイルの作成と動作確認

### 1.2 基本設計の確認

1. **既存コードの確認**
   - 現在のホロスコープ計算モジュール（`app/horoscope.py`）
   - 解釈テキスト生成モジュール（`app/interpretations.py`）
   - UI表示コントローラ（`app/routes.py`）

2. **拡張ポイントの特定**
   - 新機能追加用のPythonモジュール構成
   - フロントエンドへの統合点

3. **コーディング規約の確認**
   - PEP 8に準拠したコーディングスタイル
   - ドキュメント文字列（docstring）の形式
   - 単体テストの作成方針

## 2. サターンリターン機能の実装

### 2.1 計算ロジックの実装

1. **計算モジュールの作成**
   ```python
   # app/predictions.py
   def calculate_saturn_return(birth_date, birth_time, lat, lng):
       """サターンリターンの計算を行う
       
       Args:
           birth_date (datetime.date): 生年月日
           birth_time (datetime.time): 生まれた時間
           lat (float): 緯度
           lng (float): 経度
           
       Returns:
           dict: サターンリターン情報
       """
       # 実装内容
   ```

2. **主要機能の実装**
   - ネイタルサターン位置計算
   - 各サターンリターン時期の算出（第1回、第2回、第3回）
   - 影響期間（±6ヶ月）の計算

3. **解釈文生成機能の実装**
   ```python
   def get_saturn_return_interpretation(saturn_house, saturn_sign, saturn_aspects):
       """サターンリターンの解釈文を生成
       
       Args:
           saturn_house (int): サターンのハウス位置
           saturn_sign (str): サターンのサイン
           saturn_aspects (list): サターンの主要アスペクト
           
       Returns:
           str: 解釈文
       """
       # 実装内容
   ```

### 2.2 フロントエンド統合

1. **ルートハンドラの追加**
   ```python
   # app/routes.py
   @app.route('/saturn_return', methods=['POST'])
   def saturn_return():
       # フォームデータ取得
       # サターンリターン計算
       # テンプレートにデータ渡し
   ```

2. **テンプレートの作成**
   ```html
   <!-- app/templates/saturn_return.html -->
   {% extends "base.html" %}
   {% block content %}
     <!-- サターンリターン表示テンプレート -->
   {% endblock %}
   ```

3. **UI要素の統合**
   - メインメニューにサターンリターンオプション追加
   - 結果画面へのリンク設定

## 3. プログレッション拡張機能の実装

### 3.1 計算ロジック

1. **既存プログレッション機能の拡張**
   ```python
   # app/progressions.py
   def calculate_solar_arc(birth_date, birth_time, target_date, lat, lng):
       """ソーラーアークプログレッションの計算
       
       Args:
           birth_date (datetime.date): 生年月日
           birth_time (datetime.time): 生まれた時間
           target_date (datetime.date): 計算対象日
           lat (float): 緯度
           lng (float): 経度
           
       Returns:
           dict: ソーラーアークプログレッション情報
       """
       # 実装内容
   ```

2. **シンボリックプログレッション実装**
   ```python
   def calculate_symbolic_progression(birth_date, symbol_type, target_date):
       """シンボリックプログレッションの計算
       
       Args:
           birth_date (datetime.date): 生年月日
           symbol_type (str): シンボルタイプ ('day_for_year', 'degree_for_year')
           target_date (datetime.date): 計算対象日
           
       Returns:
           dict: シンボリックプログレッション情報
       """
       # 実装内容
   ```

### 3.2 フロントエンド統合

1. **プログレッションオプション拡張**
   - 進行法選択UI要素の追加
   - 計算パラメータ設定フォーム

2. **結果表示の実装**
   - プログレッション天体表
   - 解釈文表示

## 4. リターントランジット機能の実装

### 4.1 計算ロジック

1. **ソーラーリターン計算**
   ```python
   # app/returns.py
   def calculate_solar_return(birth_date, birth_time, target_year, lat, lng):
       """ソーラーリターンの計算
       
       Args:
           birth_date (datetime.date): 生年月日
           birth_time (datetime.time): 生まれた時間
           target_year (int): 計算対象年
           lat (float): 緯度
           lng (float): 経度
           
       Returns:
           dict: ソーラーリターン情報
       """
       # 実装内容
   ```

2. **ルナーリターン計算**
   ```python
   def calculate_lunar_return(birth_date, birth_time, target_month, lat, lng):
       """ルナーリターンの計算
       
       Args:
           birth_date (datetime.date): 生年月日
           birth_time (datetime.time): 生まれた時間
           target_month (datetime.date): 計算対象月
           lat (float): 緯度
           lng (float): 経度
           
       Returns:
           dict: ルナーリターン情報
       """
       # 実装内容
   ```

### 4.2 フロントエンド統合

1. **リターン計算フォームの作成**
   - 年次・月次選択UI
   - 場所指定オプション

2. **結果表示テンプレートの実装**
   - リターンチャート表示
   - 年間予測レポート表示

## 5. 複合的予測システムの実装

### 5.1 計算ロジック

1. **プロフェクション計算**
   ```python
   # app/ancient_techniques.py
   def calculate_annual_profections(birth_date, birth_time, target_date, asc_degree):
       """アニュアルプロフェクションの計算
       
       Args:
           birth_date (datetime.date): 生年月日
           birth_time (datetime.time): 生まれた時間
           target_date (datetime.date): 計算対象日
           asc_degree (float): 上昇度数
           
       Returns:
           dict: プロフェクション情報
       """
       # 実装内容
   ```

2. **統合予測タイムライン**
   ```python
   def generate_prediction_timeline(birth_data, start_date, end_date):
       """複数予測技法を統合したタイムライン生成
       
       Args:
           birth_data (dict): 出生データ
           start_date (datetime.date): 開始日
           end_date (datetime.date): 終了日
           
       Returns:
           dict: 予測タイムライン
       """
       # 実装内容
   ```

### 5.2 フロントエンド統合

1. **タイムライン表示の実装**
   - 時系列予測イベント表示
   - 重要時期ハイライト機能

2. **予測強度グラフの実装**
   - Matplotlibを使用した予測強度グラフ
   - インタラクティブ操作機能

## 6. 人生の重要イベント予測拡張の実装

### 6.1 予測アルゴリズム

1. **結婚時期予測アルゴリズム**
   ```python
   # app/life_events.py
   def predict_relationship_periods(birth_chart, transit_range):
       """結婚・重要な関係性の時期予測
       
       Args:
           birth_chart (dict): ネイタルチャートデータ
           transit_range (tuple): 予測範囲 (開始日, 終了日)
           
       Returns:
           list: 予測期間リスト
       """
       # 実装内容
   ```

2. **キャリア転機予測アルゴリズム**
   ```python
   def predict_career_periods(birth_chart, transit_range):
       """キャリア転機の時期予測
       
       Args:
           birth_chart (dict): ネイタルチャートデータ
           transit_range (tuple): 予測範囲 (開始日, 終了日)
           
       Returns:
           list: 予測期間リスト
       """
       # 実装内容
   ```

### 6.2 フロントエンド統合

1. **予測結果表示UI**
   - 期間ハイライトカレンダー
   - 詳細予測文表示

2. **フィルタリングと優先度表示**
   - 予測重要度によるフィルタリング
   - カスタムカテゴリ選択

## 7. テスト

### 7.1 単体テスト

1. **計算モジュールのテスト**
   ```python
   # tests/test_predictions.py
   def test_saturn_return_calculation():
       # テストケース実装
   
   def test_progression_calculations():
       # テストケース実装
   ```

2. **解釈生成のテスト**
   ```python
   # tests/test_interpretations.py
   def test_saturn_return_interpretation():
       # テストケース実装
   ```

### 7.2 統合テスト

1. **エンドツーエンドテスト**
   ```python
   # tests/test_prediction_features.py
   def test_saturn_return_workflow():
       # 入力からUI表示までのテスト
   ```

2. **クロスブラウザテスト**
   - Chrome、Firefox、Safari、Edgeでの表示テスト
   - モバイル表示テスト

## 8. デプロイ

### 8.1 データベース更新

1. **データベーススキーマ更新**
   ```sql
   -- migrations/prediction_tables.sql
   CREATE TABLE IF NOT EXISTS saturn_returns (
     id INTEGER PRIMARY KEY,
     user_id INTEGER,
     first_return_date DATE,
     first_return_interpretation TEXT,
     second_return_date DATE,
     second_return_interpretation TEXT,
     FOREIGN KEY (user_id) REFERENCES users(id)
   );
   
   -- 他のテーブル定義
   ```

2. **マイグレーションスクリプト実行**

### 8.2 本番環境デプロイ

1. **ステージング環境でのテスト**
   - 機能テスト
   - パフォーマンステスト

2. **本番デプロイ**
   - コード変更のマージ
   - データベースマイグレーション
   - 静的アセット更新

## 9. 開発スケジュール

| フェーズ | タスク | 期間 | 担当者 |
|---------|-------|------|--------|
| 1 | 設計と環境構築 | 1週間 | チーム全体 |
| 2 | サターンリターン機能実装 | 2週間 | バックエンド担当 |
| 3 | プログレッション機能拡張 | 2週間 | バックエンド担当 |
| 4 | リターントランジット実装 | 2週間 | バックエンド担当 |
| 5 | 複合予測システム実装 | 3週間 | バックエンド担当 |
| 6 | 人生イベント予測拡張 | 2週間 | バックエンド担当 |
| 7 | フロントエンド統合 | 4週間 | フロントエンド担当 |
| 8 | テスト期間 | 2週間 | QA担当 |
| 9 | ドキュメント作成 | 1週間 | ドキュメント担当 |
| 10 | デプロイ準備 | 1週間 | インフラ担当 |

## 10. 注意事項

1. **天文計算の精度**
   - Swiss Ephemerisの精度制限を理解しておく
   - 歴史的な日付（1900年以前）での計算精度に注意

2. **パフォーマンス考慮事項**
   - 重い計算はバックグラウンドジョブで実行
   - 計算結果のキャッシュ戦略を検討

3. **占星術理論の扱い**
   - 解釈は学派によって異なる可能性がある
   - ユーザーの占星術知識レベルに合わせた情報提供 