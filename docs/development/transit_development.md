# トランジット（経過）機能 開発手順書

## 1. 概要

この手順書は、ホロスコープ計算アプリケーションにトランジット（経過）計算・表示機能を追加するための開発手順を記述する。

## 2. 開発環境

既存のプロジェクト環境（Python, Flask, swisseph, etc.）を使用する。

## 3. バックエンド実装 (`utils.py`)

1.  **トランジット計算関数の作成:**
    -   `calculate_transits(jd_ut_transit, natal_point_angles_raw)` という新しい関数を作成する。
    -   引数:
        -   `jd_ut_transit`: トランジット日時（ユリウス日UT）。
        -   `natal_point_angles_raw`: ネイタルチャートの天体・感受点の生の角度（黄経）を含む辞書（`calculate_horoscope`内で生成されるものと同様）。
    -   処理内容:
        -   `jd_ut_transit` を使用し、`swe.calc_ut` でトランジット天体（太陽～冥王星）の位置（黄経）を計算する。
        -   トランジット天体の位置と、引数で受け取った `natal_point_angles_raw` を使用して、トランジット天体とネイタル感受点間のアスペクトを計算する（既存の `calculate_aspects` 関数を参考に、組み合わせを変更して実装するか、新しいアスペクト計算関数を作成する）。アスペクト計算時には、トランジット用オーブを設定する（ネイタル間より狭いオーブを使うことが多い）。
        -   計算したトランジット天体の位置情報（フォーマット済み文字列の辞書）と、トランジット-ネイタルアスペクト情報（リスト）を辞書形式で返す。
    -   戻り値（例）:
        ```python
        {
            'transit_positions': {'太陽': '牡羊座 10°25'', '月': ...},
            'transit_aspects': [
                {'t_point': '太陽', 'n_point': '金星', 'type': 'Trine', 'orb': 0.5, 'symbol': '△'},
                ...
            ]
        }
        ```
2.  **既存関数のインポート/定数確認:**
    -   必要に応じて `swe`, `PLANETS`, `POINT_NAMES_JP`, `SIGNS`, `format_degree`, `ASPECTS`, `calculate_angular_difference` などを `calculate_transits` 関数内で利用できるようにする。
    -   トランジット用のアスペクトオーブを定数として定義する（例: `TRANSIT_ASPECT_ORBS`）。

## 4. バックエンド実装 (`app.py`)

1.  **トランジット日付入力の処理:**
    -   `/` ルート:
        -   トランジット日付のデフォルト値（今日）を `index.html` に渡す（既存の `today_date` を流用または別途用意）。
    -   `/calculate` ルート:
        -   `request.form` からトランジット日付 (`transit_date`) を取得する。
        -   取得した日付文字列を `datetime` オブジェクトに変換し、`calculate_julian_day` を使ってユリウス日 `jd_ut_transit` を計算する。
        -   もし日付が入力されなかった、または不正だった場合は、デフォルト値（今日）を使用するか、エラー処理を行う。
2.  **トランジット計算の呼び出し:**
    -   `/calculate` ルート内で、ネイタルチャート計算 (`calculate_horoscope`) を実行した後、その結果からネイタルの生の角度情報 (`horoscope_data['point_angles_raw']` など、必要なら `calculate_horoscope` の戻り値に追加する必要あり) を取得する。
    -   `utils.calculate_transits(jd_ut_transit, natal_point_angles_raw)` を呼び出し、トランジットデータを取得する。
3.  **テンプレートへのデータ渡し:**
    -   `render_template` に渡す `result` 辞書に、取得したトランジットデータ（例: `result['transit_data'] = transit_data`）を追加する。
    -   トランジット計算の基準日も `result` に含めて表示できるようにする（例: `result['transit_date'] = transit_date_str`）。

## 5. フロントエンド実装 (`index.html`)

1.  **入力フィールドの追加:**
    -   生年月日、出生時間、出生地の入力フォームの下あたりに、トランジット日付を入力するための `<input type="date">` を追加する。
    -   `name="transit_date"` を設定する。
    -   サーバーから渡されたデフォルト日付 (`today_date`) を `value` 属性に設定する。
    -   ラベル (`<label for="transit_date">`) を追加する。

## 6. フロントエンド実装 (`result.html`)

1.  **トランジット情報表示セクションの追加:**
    -   「トランジット天体の位置」という見出し (`<h2>`) を持つ新しい `<div class="result-section">` を追加する。
    -   その中に、`result.transit_data.transit_positions` をループ処理し、トランジット天体のサインと度数を表示するテーブル (`<table>`) を作成する。
    -   「トランジット - ネイタル アスペクト」という見出し (`<h2>`) を持つ新しい `<div class="result-section">` を追加する。
    -   その中に、`result.transit_data.transit_aspects` をループ処理し、トランジット天体、アスペクト記号、ネイタル天体/感受点、種類、オーブをリスト (`<ul><li>`) で表示する。
    -   トランジット計算の基準日 (`result.transit_date`) をどこかに表示する。
2.  **スタイルの調整:**
    -   必要に応じて `style.css` を編集し、新しく追加したテーブルやリストの見た目を整える。

## 7. テスト

-   トランジット日付を指定した場合としない場合（デフォルト）で正しく動作するか確認する。
-   未来や過去の日付を指定して、天体位置やアスペクトが計算されるか確認する。
-   ネイタルチャートのみの場合と比較して、表示が崩れていないか確認する。
-   不正な日付を入力した場合のエラー処理を確認する。

## 8. ドキュメント

-   コード内に適切なコメントを追加する。
-   (必要であれば) `README.md` などに関連する情報を追記する。 