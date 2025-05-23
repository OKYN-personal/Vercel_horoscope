# PDF出力機能 開発手順書

## 1. 概要

この手順書は、ウェブアプリケーションに特定のPDFファイル (`horoscope_1978-05-16.pdf` および `horoscope_result.pdf`) のダウンロード機能を追加するための開発手順を記述します。
既存のFlaskアプリケーションの構造を想定しています。

## 2. 開発環境

-   Python
-   Flask
-   HTML, CSS

## 3. ファイル準備

1.  **PDFファイルの配置:**
    -   プロジェクトの `static` ディレクトリ内に、PDFファイルを格納するためのサブディレクトリを作成します（例: `static/pdf/`）。
    -   `horoscope_1978-05-16.pdf` と `horoscope_result.pdf` を作成したサブディレクトリに配置します。

## 4. バックエンド実装 (Flaskアプリケーション: `app.py`など)

1.  **ダウンロードルートの作成 (任意だが推奨):**
    -   PDFファイルへの直接リンク (`<a href="{{ url_for('static', filename='pdf/horoscope_1978-05-16.pdf') }}">`) でもダウンロードは可能ですが、ファイル名変更の容易さや、将来的なアクセス制御の導入を考慮し、専用のダウンロードルートを作成することを推奨します。
    -   例として、以下のようなルートをFlaskアプリケーションに追加します。

    ```python
    from flask import send_from_directory
    import os

    # ... (Flask app 初期化) ...

    PDF_DIRECTORY = os.path.join(app.root_path, 'static', 'pdf')

    @app.route('/download_pdf/<filename>')
    def download_pdf(filename):
        # セキュリティのため、ファイル名が無害であることを確認する（例: ../ を含まないなど）
        # ここでは単純化のため、許可するファイル名を固定
        allowed_files = ['horoscope_1978-05-16.pdf', 'horoscope_result.pdf']
        if filename not in allowed_files:
            return "File not found or access denied", 404
        try:
            return send_from_directory(PDF_DIRECTORY, filename, as_attachment=True)
        except FileNotFoundError:
            # app.logger.error(f"PDF file not found: {filename}") # エラーログ
            return "File not found", 404
    ```

2.  **ルートの登録:**
    -   上記で作成した関数を、Flaskアプリケーションのルートとして登録します。

## 5. フロントエンド実装 (HTMLテンプレート: 例 `index.html` や専用ページ)

1.  **ダウンロードリンクの設置:**
    -   ユーザーがPDFをダウンロードできるページ（例: `/` ルートの `index.html` や、新しく作成する `/downloads` ページなど）に、各PDFへのダウンロードリンクを追加します。
    -   バックエンドで専用ルートを作成した場合:
        ```html
        <h2>PDFダウンロード</h2>
        <ul>
            <li><a href="{{ url_for('download_pdf', filename='horoscope_1978-05-16.pdf') }}">ホロスコープサンプル (1978-05-16) をダウンロード</a></li>
            <li><a href="{{ url_for('download_pdf', filename='horoscope_result.pdf') }}">ホロスコープ結果サンプルをダウンロード</a></li>
        </ul>
        ```
    -   `static` ディレクトリへ直接リンクする場合:
        ```html
        <h2>PDFダウンロード</h2>
        <ul>
            <li><a href="{{ url_for('static', filename='pdf/horoscope_1978-05-16.pdf') }}" download>ホロスコープサンプル (1978-05-16) をダウンロード</a></li>
            <li><a href="{{ url_for('static', filename='pdf/horoscope_result.pdf') }}" download>ホロスコープ結果サンプルをダウンロード</a></li>
        </ul>
        <!-- 'download' 属性は、ブラウザにファイルをダウンロードするよう促しますが、
             サーバーサイドで Content-Disposition を設定する方が確実です -->
        ```

2.  **表示とスタイル:**
    -   必要に応じて、ダウンロードセクションやリンクの見た目をCSSで調整します。

## 6. テスト

-   指定したPDFファイル (`horoscope_1978-05-16.pdf`, `horoscope_result.pdf`) が正しくダウンロードされることを確認します。
-   ダウンロードされるファイル名が正しいことを確認します。
-   ファイルが破損していないことを確認します（ダウンロード後に開いて確認）。
-   存在しないファイル名を指定した場合（もしバックエンドルートを汎用的にした場合）や、ファイルが実際にサーバーに存在しない場合に、適切なエラーメッセージ（例: 404 Not Found）が返されることを確認します。
-   リンクの表示やテキストが要件通りであることを確認します。

## 7. ドキュメント

-   コード内に適切なコメントを追加します。
-   (必要であれば) `README.md` などに機能に関する説明を追記します。 