from weasyprint import HTML
from flask import render_template # render_template を直接インポート
from datetime import datetime
import os
import traceback

# アプリケーションのルートパスからの相対パスを使用するように変更
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(APP_ROOT, 'static', 'pdfs')

def generate_horoscope_pdf(data, output_dir=DEFAULT_OUTPUT_DIR):
    """ホロスコープPDFを生成する"""
    try:
        # 出力ディレクトリの作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 現在時刻を取得
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        
        # ファイル名の生成
        filename = f'horoscope_{timestamp}.pdf'
        output_path = os.path.join(output_dir, filename)
        
        # テンプレートに渡すデータを準備 (prepare_template_dataは不要に)
        # data辞書に必要な情報が含まれている前提
        template_data = data.copy() # 元のdataを変更しないようにコピー
        template_data['generated_at'] = now.strftime('%Y-%m-%d %H:%M:%S')

        # HTMLテンプレートのレンダリング
        html_string = render_template('horoscope_pdf.html', **template_data)

        # デバッグ用
        # print("--- Template Data ---")
        # import json
        # print(json.dumps(template_data, indent=2, ensure_ascii=False))
        # print("--- HTML Content ---")
        # print(html_string)
        # print("--- End HTML Content ---")

        html = HTML(string=html_string)
        
        # PDFの生成
        html.write_pdf(output_path)
        
        return filename
    except Exception as e:
        print(f"Error during PDF generation: {e}")
        traceback.print_exc()
        raise

# prepare_template_data 関数は不要になったため削除
# render_horoscope_template 関数も不要になったため削除 