# ホロスコープ計算アプリケーション - アーキテクチャと機能概要

## アプリケーション概要

このアプリケーションは、占星術のホロスコープを計算・表示するWebアプリケーションです。ユーザーの生年月日、出生時間、出生地を入力することでネイタルチャート（出生図）を生成し、トランジット（現在や指定日の天体配置）との関係も計算・表示します。

主な機能として、天体の位置計算、ハウス計算、アスペクト（天体間の角度関係）計算、および各要素の占星術的解釈の表示があります。

## システムアーキテクチャ

アプリケーションは以下の構成で実装されています：

```
クライアント（ブラウザ） <--> Flask Webサーバー <--> 天体計算ライブラリ（swisseph）
                                      |
                                      +--> 外部API（Google Maps API）
```

### バックエンド

- **Flask**：Webフレームワーク
- **Swiss Ephemeris (swisseph)**：高精度な天体位置計算ライブラリ
- **Python**：メインのプログラミング言語

### フロントエンド

- **HTML/CSS**：ユーザーインターフェース
- **JavaScript/jQuery**：クライアント側の動的機能
- **Google Maps JavaScript API**：位置情報の検索と緯度経度の取得

## 技術スタック

| 技術/ライブラリ | 用途 |
|--------------|------|
| Python 3.x | バックエンド開発言語 |
| Flask | Webアプリケーションフレームワーク |
| Jinja2 | HTMLテンプレートエンジン |
| swisseph | 天体位置計算ライブラリ |
| JavaScript/jQuery | フロントエンドのインタラクション |
| Google Maps API | 地名検索・位置情報取得 |
| HTML5/CSS3 | フロントエンド表示 |

## 主要機能

### 1. ネイタルチャート計算
- 生年月日、出生時間、出生地に基づく天体位置計算
- ハウスシステム（Placidus、Koch、Regiomontanus等）に基づくハウス計算
- 天体間アスペクト（角度関係）の計算

### 2. 地理位置情報検索と緯度経度変換
- Google Maps Place Autocomplete APIを使用した地名検索
- 地名から緯度経度への変換
- 日本の主要都市データベースによる位置情報検索

### 3. トランジット計算
- 指定日時（デフォルトは現在）の天体位置計算
- ネイタルチャートとトランジットの天体間アスペクト計算

### 4. 占星術解釈
- 天体のサイン（星座）における解釈
- 天体のハウスにおける解釈
- 天体間アスペクトの解釈（静的・動的生成）
- トランジット天体とネイタル天体間アスペクトの解釈

### 5. チャート表示
- 円形チャート表示
- アスペクトグリッド表示
- 天体位置リスト表示

## ディレクトリ構造

```
horoscope/
├── app/
│   ├── __init__.py        # アプリケーション初期化
│   ├── routes.py          # ルーティング処理
│   ├── utils.py           # ユーティリティ関数
│   ├── utils/
│   │   ├── aspects.py     # アスペクト計算関連
│   │   └── ...            # その他のユーティリティ
│   ├── geocoding.py       # 地名-位置情報変換機能
│   ├── interpretations.py # 占星術解釈データと関数
│   ├── static/
│   │   ├── css/           # スタイルシート
│   │   ├── js/            # JavaScript
│   │   └── images/        # 画像ファイル
│   └── templates/
│       ├── index.html     # 入力フォームページ
│       ├── result.html    # 結果表示ページ
│       └── ...            # その他のテンプレート
├── requirements.txt       # 依存パッケージリスト
└── run.py                 # アプリケーション起動スクリプト
```

## 特筆すべき実装

### アスペクト解釈の動的生成システム

データベースに予め登録されていないアスペクト組み合わせに対して、天体の基本特性とアスペクトの性質を組み合わせて自動的に解釈文を生成するシステムを実装しています。

```python
PLANET_QUALITIES = {
    "Sun": {
        "name_jp": "太陽",
        "keywords": "自己表現、アイデンティティ、創造性...",
        "positive": "自信、リーダーシップ、創造力...",
        "negative": "傲慢、支配的、自己中心的..."
    },
    # 他の天体も同様...
}

ASPECT_QUALITIES = {
    "conjunction": {
        "name_jp": "コンジャンクション",
        "keywords": "結合、一体化、強調...",
        "nature": "中性（天体により変化）",
        "description": "二つの天体のエネルギーが融合し..."
    },
    # 他のアスペクトも同様...
}

def get_dynamic_aspect_interpretation(planet1, planet2, aspect_type):
    # 天体とアスペクトの特性に基づいて解釈文を動的に生成
    # ...
```

### Google Maps API 統合

ユーザーが地名を入力すると候補を表示し、選択時に自動的に緯度経度を取得・設定する機能：

```javascript
// Google Maps Place Autocomplete APIの初期化と設定
function initAutocomplete() {
    const input = document.getElementById('location_input');
    const autocomplete = new google.maps.places.Autocomplete(input);
    
    // 場所が選択されたときのイベントリスナー
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (place.geometry) {
            // 緯度経度フィールドに値をセット
            document.getElementById('latitude').value = place.geometry.location.lat();
            document.getElementById('longitude').value = place.geometry.location.lng();
            // フィードバック表示
            document.getElementById('location_feedback').textContent = 
                `位置情報を取得しました: ${place.formatted_address}`;
        }
    });
}
```

## 今後の拡張方向

1. **進行（プログレッション）機能**: 時間の進行に伴う天体移動の計算・表示機能
2. **相性（シナストリー）機能**: 2人の出生図を比較し相性を解析する機能
3. **リターン計算**: サターンリターン、ジュピターリターンなどの特定天体の周期的な回帰点計算
4. **PDFエクスポート**: チャートと解釈の詳細なPDFレポート生成機能
5. **ユーザーアカウント**: 複数のチャートを保存・管理する機能
6. **モバイル対応の改善**: レスポンシブデザインの強化

## 技術的課題と解決方法

1. **地名と緯度経度の不一致問題**
   - 解決策: 日本の主要都市データベースの実装と、Google Maps API統合

2. **アスペクト解釈の網羅性**
   - 解決策: 天体とアスペクトの基本特性を元にした動的解釈生成システム

3. **環境変数管理**
   - 解決策: 外部APIキーやパスワードなどを環境変数で管理

4. **UI/UXの改善**
   - 解決策: ユーザビリティを考慮したフォームデザイン、ヘルプテキスト、エラーハンドリングの実装 