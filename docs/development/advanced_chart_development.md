# 高度なチャート表示 開発手順書

## 1. 開発準備

### 1.1 開発環境構築

1. **リポジトリのクローンと専用ブランチ作成**
   ```bash
   git clone https://github.com/yourusername/stargazer.git
   cd stargazer
   git checkout -b feature/advanced-charts
   ```

2. **依存パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   # 追加のフロントエンド開発ツール
   npm install d3 chart.js svg.js
   ```

3. **開発サーバー起動**
   ```bash
   python app.py
   ```

### 1.2 既存コード調査

1. **現行チャート実装の確認**
   - `app/static/js/chart.js`: 現在のホロスコープチャート描画コード
   - `app/templates/result.html`: 結果表示テンプレート
   - `app/static/css/style.css`: チャート表示用スタイル

2. **拡張ポイントの特定**
   - SVG生成関数の拡張可能性
   - フロントエンドコンポーネント構成
   - バックエンドとのデータ連携方法

## 2. 三重円チャート機能の実装

### 2.1 バックエンド対応

1. **データ構造の拡張**
   ```python
   # app/horoscope.py
   def prepare_multi_chart_data(natal_data, progression_data=None, transit_data=None):
       """三重円チャート用データの準備
       
       Args:
           natal_data (dict): ネイタルチャートデータ
           progression_data (dict, optional): プログレッションデータ
           transit_data (dict, optional): トランジットデータ
           
       Returns:
           dict: 三重円チャート用の統合データ
       """
       # データ整形処理
       return formatted_data
   ```

2. **ルートハンドラの拡張**
   ```python
   # app/routes.py
   @app.route('/multi_chart', methods=['POST'])
   def multi_chart():
       # ユーザー入力データの取得
       # 各チャートの計算
       # 三重円チャート用データ準備
       # テンプレートにデータ渡し
   ```

### 2.2 フロントエンド実装

1. **SVG生成関数の作成**
   ```javascript
   // app/static/js/multi_chart.js
   function renderMultiChart(chartData, containerId, options) {
     // SVG要素の作成
     // 同心円の描画
     // 各層ごとの天体配置
     // ハウスカスプ線の描画
     // アスペクト線の描画
   }
   ```

2. **コントロールUIの実装**
   ```html
   <!-- app/templates/multi_chart.html -->
   <div class="chart-controls">
     <div class="layer-selector">
       <!-- チャート層選択UI -->
     </div>
     <div class="filter-controls">
       <!-- 天体フィルターUI -->
     </div>
   </div>
   ```

3. **レスポンシブ対応**
   ```css
   /* app/static/css/multi_chart.css */
   .multi-chart-container {
     width: 100%;
     max-width: 800px;
     margin: 0 auto;
   }
   
   @media (max-width: 768px) {
     /* モバイル対応スタイル */
   }
   ```

## 3. アスペクトパターン検出機能の実装

### 3.1 バックエンド実装

1. **パターン検出アルゴリズム**
   ```python
   # app/aspect_patterns.py
   def detect_aspect_patterns(aspects_list):
       """アスペクトリストからパターンを検出
       
       Args:
           aspects_list (list): アスペクトのリスト
           
       Returns:
           list: 検出されたパターンのリスト
       """
       patterns = []
       
       # グランドトライン検出
       grand_trines = detect_grand_trines(aspects_list)
       patterns.extend(grand_trines)
       
       # Tスクエア検出
       t_squares = detect_t_squares(aspects_list)
       patterns.extend(t_squares)
       
       # ヨッド検出
       yods = detect_yods(aspects_list)
       patterns.extend(yods)
       
       return patterns
   ```

2. **パターン解釈生成**
   ```python
   # app/interpretations.py
   def get_pattern_interpretation(pattern_type, planets_involved):
       """アスペクトパターンの解釈を生成
       
       Args:
           pattern_type (str): パターンのタイプ
           planets_involved (list): 関与する天体
           
       Returns:
           str: パターンの解釈文
       """
       # 解釈生成ロジック
   ```

### 3.2 フロントエンド実装

1. **パターン視覚化**
   ```javascript
   // app/static/js/aspect_patterns.js
   function highlightPattern(pattern, chartSvg) {
     // パターンに関与する天体とアスペクトをハイライト
     // パターン固有の視覚化
   }
   ```

2. **パターンリスト表示UI**
   ```html
   <!-- app/templates/patterns_section.html -->
   <div class="patterns-container">
     <h3>検出されたパターン</h3>
     <ul class="patterns-list">
       {% for pattern in patterns %}
         <li class="pattern-item" data-pattern-id="{{ pattern.id }}">
           <!-- パターン情報表示 -->
         </li>
       {% endfor %}
     </ul>
   </div>
   ```

## 4. 調和分析チャート機能の実装

### 4.1 バックエンド実装

1. **エレメント分布計算**
   ```python
   # app/harmony_analysis.py
   def calculate_element_distribution(chart_data):
       """エレメント（火・地・風・水）の分布を計算
       
       Args:
           chart_data (dict): チャートデータ
           
       Returns:
           dict: エレメント分布データ
       """
       # 分布計算ロジック
   ```

2. **モダリティ分布計算**
   ```python
   def calculate_modality_distribution(chart_data):
       """モダリティ（活動宮・不動宮・柔軟宮）の分布を計算
       
       Args:
           chart_data (dict): チャートデータ
           
       Returns:
           dict: モダリティ分布データ
       """
       # 分布計算ロジック
   ```

3. **天体強度計算**
   ```python
   def calculate_planet_strength(chart_data):
       """天体の強度を計算
       
       Args:
           chart_data (dict): チャートデータ
           
       Returns:
           dict: 天体強度データ
       """
       # 強度計算ロジック（エッセンシャル・ディグニティ、ハウス位置、アスペクト等）
   ```

### 4.2 フロントエンド実装

1. **分布チャート作成**
   ```javascript
   // app/static/js/harmony_charts.js
   function renderElementChart(elementData, containerId) {
     // Chart.jsを使用した円グラフ・棒グラフ生成
   }
   
   function renderModalityChart(modalityData, containerId) {
     // Chart.jsを使用した円グラフ・棒グラフ生成
   }
   ```

2. **ディスポジター分析図**
   ```javascript
   function renderDispositorChart(dispositorData, containerId) {
     // 天体の支配連鎖を示すグラフ生成
     // D3.jsを使用した有向グラフ
   }
   ```

## 5. アラビックパーツと固定星機能の実装

### 5.1 バックエンド実装

1. **アラビックパーツ計算**
   ```python
   # app/arabic_parts.py
   def calculate_arabic_parts(chart_data):
       """主要なアラビックパーツを計算
       
       Args:
           chart_data (dict): チャートデータ
           
       Returns:
           dict: アラビックパーツデータ
       """
       parts = {}
       
       # 運命の車輪 (Pars Fortunae)
       parts['fortune'] = calculate_part_of_fortune(
           chart_data['asc_degree'],
           chart_data['planets']['sun']['position'],
           chart_data['planets']['moon']['position']
       )
       
       # 他のパーツ計算
       
       return parts
   ```

2. **固定星計算**
   ```python
   # app/fixed_stars.py
   def calculate_fixed_star_conjunctions(chart_data, orb=1.0):
       """主要固定星との合を計算
       
       Args:
           chart_data (dict): チャートデータ
           orb (float): 許容オーブ（角度）
           
       Returns:
           list: 固定星合のリスト
       """
       # 固定星位置と天体位置の比較
   ```

### 5.2 フロントエンド実装

1. **パーツと固定星の表示**
   ```javascript
   // app/static/js/special_points.js
   function renderArabicParts(partsData, chartSvg) {
     // アラビックパーツのシンボル描画
   }
   
   function renderFixedStars(starsData, chartSvg) {
     // 固定星の表示
   }
   ```

2. **解釈テキスト表示**
   ```html
   <!-- app/templates/special_points.html -->
   <div class="special-points-container">
     <div class="arabic-parts">
       <!-- アラビックパーツ情報表示 -->
     </div>
     <div class="fixed-stars">
       <!-- 固定星情報表示 -->
     </div>
   </div>
   ```

## 6. ダイナミックタイムマップ機能の実装

### 6.1 バックエンド実装

1. **時系列トランジットデータ生成**
   ```python
   # app/time_map.py
   def generate_transit_timeline(birth_data, start_date, end_date, step_days=1):
       """時系列トランジットデータを生成
       
       Args:
           birth_data (dict): 出生データ
           start_date (datetime.date): 開始日
           end_date (datetime.date): 終了日
           step_days (int): 何日単位で計算するか
           
       Returns:
           dict: 時系列データ
       """
       # 期間内の各日付でのトランジット計算
   ```

2. **アスペクト強度計算**
   ```python
   def calculate_aspect_intensity(natal_data, transit_timeline):
       """時系列でのアスペクト強度を計算
       
       Args:
           natal_data (dict): ネイタルデータ
           transit_timeline (dict): トランジットタイムライン
           
       Returns:
           dict: 時系列アスペクト強度
       """
       # 時間による強度変化の計算
   ```

### 6.2 フロントエンド実装

1. **タイムラインチャート作成**
   ```javascript
   // app/static/js/timeline_chart.js
   function renderTimelineChart(timelineData, containerId) {
     // D3.jsを使用した時系列グラフ
     // 時間軸と強度軸
     // イベントマーカー
   }
   ```

2. **タイムスライダー実装**
   ```javascript
   function createTimeSlider(timelineData, containerId, chartId) {
     // スライダーUI実装
     // スライダー変更時のチャート更新
   }
   ```

3. **アニメーション機能**
   ```javascript
   function animateAspectChanges(timelineData, chartSvg, options) {
     // アスペクト変化のアニメーション
     // 再生・一時停止コントロール
   }
   ```

## 7. 統合とテスト

### 7.1 各機能の統合

1. **画面レイアウト設計**
   ```html
   <!-- app/templates/advanced_chart_dashboard.html -->
   <div class="chart-dashboard">
     <div class="main-chart-area">
       <!-- 三重円チャート表示エリア -->
     </div>
     <div class="analysis-panels">
       <!-- 各分析パネル（タブ形式） -->
     </div>
     <div class="timeline-area">
       <!-- タイムライン表示エリア -->
     </div>
   </div>
   ```

2. **UI状態管理**
   ```javascript
   // app/static/js/chart_state_manager.js
   class ChartStateManager {
     constructor() {
       // 状態初期化
     }
     
     updateChartLayers(visibleLayers) {
       // 表示層の更新
     }
     
     updatePlanetFilters(visiblePlanets) {
       // 表示天体フィルタリング
     }
     
     // 他の状態管理メソッド
   }
   ```

### 7.2 テスト計画

1. **機能テスト項目**
   - 三重円チャート表示テスト
   - アスペクトパターン検出テスト
   - 調和分析チャートテスト
   - アラビックパーツ・固定星テスト
   - タイムラインテスト

2. **UI/UXテスト項目**
   - レスポンシブデザインテスト
   - インタラクション応答性テスト
   - アクセシビリティテスト

3. **パフォーマンステスト項目**
   - 描画速度テスト
   - メモリ使用量テスト
   - モバイルデバイス互換性テスト

## 8. 最適化

### 8.1 パフォーマンス最適化

1. **描画処理の最適化**
   ```javascript
   // SVG要素の効率的な生成
   // レイヤー表示切替時の再描画最小化
   ```

2. **データ転送量の削減**
   ```python
   # 必要データのみをフロントエンドに送信
   # データ構造の最適化
   ```

3. **キャッシュ戦略**
   ```javascript
   // 計算済みチャートのキャッシュ
   // プリレンダリング
   ```

### 8.2 モバイル最適化

1. **タッチインターフェース対応**
   ```javascript
   // タッチ操作検出
   // ピンチズーム実装
   ```

2. **表示領域の調整**
   ```css
   /* スクリーンサイズに応じた要素配置 */
   /* フォントサイズの動的調整 */
   ```

## 9. ドキュメント作成

### 9.1 コードドキュメント

1. **モジュール構成図の作成**
2. **主要関数・クラスのドキュメント**
3. **データ構造の説明**

### 9.2 ユーザーガイド

1. **各チャート機能の説明**
2. **解釈の読み方ガイド**
3. **よくある質問と回答**

## 10. 開発スケジュール

| フェーズ | タスク | 期間 | 担当者 |
|---------|-------|------|--------|
| 1 | 設計と環境構築 | 1週間 | チーム全体 |
| 2 | 三重円チャート実装 | 2週間 | フロントエンドエンジニア |
| 3 | アスペクトパターン検出 | 1週間 | バックエンド＆フロントエンド |
| 4 | 調和分析チャート | 1週間 | データ分析＆UI担当 |
| 5 | アラビックパーツと固定星 | 1週間 | バックエンド担当 |
| 6 | ダイナミックタイムマップ | 2週間 | データ可視化担当 |
| 7 | 統合とテスト | 2週間 | QA担当 |
| 8 | 最適化 | 1週間 | パフォーマンス担当 |
| 9 | ドキュメント | 1週間 | 技術ライター |

## 11. 注意事項

1. **ブラウザ互換性**
   - IEはサポート対象外
   - 最新のChrome、Firefox、Safari、Edgeをサポート

2. **モバイル対応の優先順位**
   - モバイルではシンプルな表示に切り替え
   - タッチ操作の優先的サポート

3. **デザイン統一性**
   - 既存UIとの視覚的一貫性維持
   - カラーパレットの統一 