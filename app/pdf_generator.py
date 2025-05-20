from weasyprint import HTML, CSS
from flask import render_template
from datetime import datetime
import os
import traceback
import logging

# アプリケーションのルートパスからの相対パスを使用
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(APP_ROOT, 'static', 'pdfs')

def generate_horoscope_pdf(data, output_dir=DEFAULT_OUTPUT_DIR):
    """ホロスコープPDFを生成する（改良版）"""
    try:
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 現在時刻を取得
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        
        # ファイル名の生成 (ユニーク化)
        if 'birth_date' in data and 'birth_time' in data:
            birth_date_str = data['birth_date'].replace('-', '')
            birth_time_str = data['birth_time'].replace(':', '')
            filename = f'horoscope_{birth_date_str}_{birth_time_str}_{timestamp}.pdf'
        else:
            filename = f'horoscope_{timestamp}.pdf'
        
        output_path = os.path.join(output_dir, filename)
        
        # テンプレートに渡すデータを準備
        template_data = data.copy()
        template_data['generated_at'] = now.strftime('%Y-%m-%d %H:%M:%S')

        # HTMLテンプレートのレンダリング
        html_string = render_template('horoscope_pdf.html', **template_data)

        # 追加のスタイルシートを定義
        css_string = """
            @page {
                size: A4;
                margin: 1.5cm;
                @top-center {
                    content: "ホロスコープ解釈";
                    font-size: 9pt;
                    color: #666;
                }
                @bottom-center {
                    content: "生成日時: """ + now.strftime('%Y-%m-%d %H:%M:%S') + """ / " counter(page) " / " counter(pages);
                    font-size: 9pt;
                    color: #666;
                }
            }
            body {
                font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
                line-height: 1.6;
                font-size: 10pt;
                color: #333;
            }
            .result-section {
                page-break-inside: avoid;
                margin-bottom: 1.5em;
                border-top: 1px dashed #ccc;
            }
            .chart-container svg {
                max-width: 100%;
                height: auto;
                page-break-inside: avoid;
            }
            .bookmark-section {
                page-break-before: always;
            }
            .toc {
                counter-reset: section;
                margin-bottom: 2em;
            }
            .toc-item {
                display: flex;
                align-items: baseline;
                margin-bottom: 0.5em;
            }
            .toc-number::before {
                counter-increment: section;
                content: counter(section) ". ";
            }
            .toc-title {
                flex-grow: 1;
            }
            .toc-dots {
                flex-grow: 1;
                margin: 0 0.5em;
                border-bottom: 1px dotted #ccc;
            }
            .toc-page {
                text-align: right;
            }
        """
        css = CSS(string=css_string)

        # PDFの生成
        html = HTML(string=html_string)
        # 追加のCSS、ページサイズ、メタデータを設定
        pdf = html.write_pdf(
            output_path, 
            stylesheets=[css],
            presentational_hints=True,
            optimize_size=('fonts', 'images'),
            attachments=None,  # ファイル添付が必要な場合は設定
            metadata={
                'title': f'ホロスコープ解釈 {data.get("birth_date", "")}',
                'author': 'ホロスコープ計算システム',
                'subject': f'出生図: {data.get("birth_place", "")}',
                'keywords': '占星術,ホロスコープ,アスペクト,サビアンシンボル',
                'generator': 'WeasyPrint with Flask',
                'created': now.isoformat()
            }
        )
        
        return filename
    except Exception as e:
        logging.error(f"Error during PDF generation: {e}")
        traceback.print_exc()
        raise

# prepare_template_data 関数は不要になったため削除
# render_horoscope_template 関数も不要になったため削除 