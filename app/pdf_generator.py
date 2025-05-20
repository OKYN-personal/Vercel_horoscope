from weasyprint import HTML, CSS
from flask import render_template, current_app
from datetime import datetime
import os
import traceback
import logging

# アプリケーションのルートパスからの相対パスを使用
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(APP_ROOT, 'static', 'pdfs')

# --- PDF生成の共通ヘルパー関数 ---
def _prepare_pdf_generation(output_dir_name='pdfs', filename_prefix='horoscope'):
    """PDF生成の準備（ディレクトリ作成、ファイル名生成）を行う"""
    output_dir = os.path.join(APP_ROOT, 'static', output_dir_name)
    os.makedirs(output_dir, exist_ok=True)
    
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d_%H%M%S')
    filename = f'{filename_prefix}_{timestamp}.pdf'
    output_path = os.path.join(output_dir, filename)
    return output_path, filename, now

def _write_pdf_from_html(html_string, output_path, css_string=None, metadata_override=None):
    """HTML文字列からPDFを書き出す共通処理"""
    default_css_string = """
        @page {
            size: A4;
            margin: 1.5cm;
            @top-center {
                content: var(--pdf-title, "占星術レポート");
                font-size: 9pt;
                color: #666;
            }
            @bottom-center {
                content: "生成日時: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ / " counter(page) " / " counter(pages);
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
        /* 他の共通スタイルもここに追加可能 */
    """
    final_css_string = css_string if css_string else default_css_string
    css = CSS(string=final_css_string)
    
    html = HTML(string=html_string)
    
    default_metadata = {
        'author': 'ホロスコープ計算システム',
        'generator': 'WeasyPrint with Flask',
        'created': datetime.now().isoformat()
    }
    if metadata_override:
        default_metadata.update(metadata_override)

    html.write_pdf(
        output_path, 
        stylesheets=[css],
        presentational_hints=True,
        optimize_size=('fonts', 'images'),
        metadata=default_metadata
    )

# --- ネイタルホロスコープPDF ---
def generate_horoscope_pdf(data):
    """ネイタルホロスコープPDFを生成する"""
    try:
        output_path, filename, now = _prepare_pdf_generation(filename_prefix=f"horoscope_{data.get('birth_date','').replace('-','')}_{data.get('birth_time','').replace(':','')}")
        
        template_data = data.copy()
        template_data['generated_at'] = now.strftime('%Y-%m-%d %H:%M:%S')
        
        html_string = render_template('horoscope_pdf.html', **template_data)
        
        # horoscope_pdf.html 専用のスタイルやメタデータをここで設定可能
        pdf_title = "ホロスコープ解釈"
        if 'birth_date' in data:
            pdf_title += f" - {data['birth_date']}"

        css_override = f"""
            @page {{
                @top-center {{
                    content: "{pdf_title}";
                }}
            }}
            /* horoscope_pdf.html に特化したスタイルがあればここに追加 */
        """ # 基本CSSに追加する形で

        metadata = {
            'title': f'ホロスコープ解釈 {data.get("birth_date", "")}',
            'subject': f'出生図: {data.get("birth_place", "")}',
            'keywords': '占星術,ホロスコープ,アスペクト,サビアンシンボル',
        }
        
        _write_pdf_from_html(html_string, output_path, css_string=css_override, metadata_override=metadata) # CSSは共通 + overrideで対応も可
        
        return filename
    except Exception as e:
        logging.error(f"Error during Horoscope PDF generation: {e}")
        traceback.print_exc()
        raise

# --- シナストリーPDF ---
def generate_synastry_pdf(data):
    """シナストリー（相性占い）PDFを生成する - 雛形"""
    try:
        filename_prefix = "synastry"
        if data.get('person1') and data['person1'].get('birth_date'):
            filename_prefix += f"_{data['person1']['birth_date'].replace('-','')}"
        if data.get('person2') and data['person2'].get('birth_date'):
            filename_prefix += f"_{data['person2']['birth_date'].replace('-','')}"

        output_path, filename, now = _prepare_pdf_generation(filename_prefix=filename_prefix)
        
        template_data = data.copy()
        template_data['generated_at'] = now.strftime('%Y-%m-%d %H:%M:%S')
        template_data['pdf_title'] = "シナストリー解析結果"
        
        # テンプレートに渡すデータを'result'キーの下にネストする
        html_string = render_template('synastry_pdf.html', result=template_data)
        
        pdf_title = "シナストリー解析結果"
        metadata = {
            'title': pdf_title,
            'subject': '相性占いレポート',
            'keywords': '占星術,シナストリー,相性,ホロスコープ',
        }
        
        # PDFタイトル用のCSSオーバーライドを追加
        css_override = f"""
            @page {{
                @top-center {{
                    content: "{pdf_title}";
                }}
            }}
            /* synastry_pdf.html に特化したスタイルがあればここに追加 */
        """
        
        # CSSオーバーライドを渡す
        _write_pdf_from_html(html_string, output_path, css_string=css_override, metadata_override=metadata)
        
        return filename
    except Exception as e:
        current_app.logger.error(f"Error during Synastry PDF generation: {e}\n{traceback.format_exc()}")
        raise

# --- 月のノードPDF ---
def generate_lunar_nodes_pdf(data):
    """月のノード（ドラゴンヘッド/テイル）PDFを生成する - 雛形"""
    try:
        filename_prefix = "lunar_nodes"
        if data.get('birth_date'):
            filename_prefix += f"_{data['birth_date'].strftime('%Y%m%d') if isinstance(data['birth_date'], datetime) else str(data['birth_date']).replace('-','')}"

        output_path, filename, now = _prepare_pdf_generation(filename_prefix=filename_prefix)
        
        template_data = data.copy()
        template_data['generated_at'] = now.strftime('%Y-%m-%d %H:%M:%S')

        # TODO: 月のノード用のPDFテンプレート (lunar_nodes_pdf.html) を作成する
        html_string = render_template('lunar_nodes_pdf.html', **template_data) # テンプレート名を変更

        pdf_title = "月のノード解釈"
        metadata = {
            'title': pdf_title,
            'subject': '月のノードレポート',
            'keywords': '占星術,月のノード,ドラゴンヘッド,ドラゴンテイル',
        }
        
        # PDFタイトル用のCSSオーバーライドを追加
        css_override = f"""
            @page {{
                @top-center {{
                    content: "{pdf_title}";
                }}
            }}
            /* lunar_nodes_pdf.html に特化したスタイルがあればここに追加 */
        """
        
        _write_pdf_from_html(html_string, output_path, css_string=css_override, metadata_override=metadata)
        
        return filename
    except Exception as e:
        current_app.logger.error(f"Error during Lunar Nodes PDF generation: {e}\n{traceback.format_exc()}")
        raise

# --- ライフイベントPDF ---
def generate_life_events_pdf(data):
    """ライフイベント予測PDFを生成する - 雛形"""
    try:
        filename_prefix = "life_events"
        if data.get('birth_date'):
             filename_prefix += f"_{data['birth_date'].strftime('%Y%m%d') if isinstance(data['birth_date'], datetime) else str(data['birth_date']).replace('-','')}"

        output_path, filename, now = _prepare_pdf_generation(filename_prefix=filename_prefix)
        
        template_data = data.copy()
        template_data['generated_at'] = now.strftime('%Y-%m-%d %H:%M:%S')

        # TODO: ライフイベント用のPDFテンプレート (life_events_pdf.html) を作成する
        html_string = render_template('life_events_pdf.html', **template_data) # テンプレート名を変更
        
        pdf_title = "ライフイベント予測レポート"
        metadata = {
            'title': pdf_title,
            'subject': 'ライフイベント予測',
            'keywords': '占星術,トランジット,プログレッション,予測',
        }
        
        # PDFタイトル用のCSSオーバーライドを追加
        css_override = f"""
            @page {{
                @top-center {{
                    content: "{pdf_title}";
                }}
            }}
            /* life_events_pdf.html に特化したスタイルがあればここに追加 */
        """
        
        _write_pdf_from_html(html_string, output_path, css_string=css_override, metadata_override=metadata)
        
        return filename
    except Exception as e:
        current_app.logger.error(f"Error during Life Events PDF generation: {e}\n{traceback.format_exc()}")
        raise 