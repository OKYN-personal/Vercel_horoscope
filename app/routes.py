from flask import Blueprint, render_template, request, jsonify, url_for, current_app
from datetime import datetime, timezone, timedelta
# from .utils.horoscope import calculate_planet_positions, get_sabian_symbol
# from .utils.aspects import calculate_aspects, get_aspect_description
# from app import create_app # create_appは循環参照になる可能性があるので通常routesからは呼ばない
from app.horoscope import calculate_natal_chart, calculate_transit, calculate_aspects, generate_aspect_grid, \
    calculate_solar_arc_sabian_forecast, calculate_vernal_equinox_sabian, \
    calculate_summer_solstice_sabian, calculate_autumnal_equinox_sabian, calculate_winter_solstice_sabian, \
    calculate_secondary_progression, calculate_lunar_nodes, predict_life_events, NODE_INTERPRETATIONS, get_house_number, \
    calculate_synastry as hs_calculate_synastry # calculate_synastry を hs_calculate_synastry としてインポート
from app.sabian import get_sabian_symbol # get_interpretation は削除されたのでインポートしない
from app.pdf_generator import generate_horoscope_pdf, generate_synastry_pdf, generate_lunar_nodes_pdf, generate_life_events_pdf # 新しいPDF生成関数をインポート
from app.chart_generator import generate_chart_svg # SVG生成関数をインポート
from app.interpretations import PLANET_IN_SIGN_INTERPRETATIONS, PLANET_IN_HOUSE_INTERPRETATIONS, ASPECT_INTERPRETATIONS # ASPECT_INTERPRETATIONS を追加
from app.utils import get_city_coordinates # , calculate_timezone_offset # calculate_timezone_offset を一旦コメントアウト
from app.geocoding import get_coordinates_from_google_maps # Google Maps APIを使う関数をインポート
import os
import traceback # tracebackモジュールをインポート
import swisseph as swe # swissephをインポート

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Google Maps APIキーをテンプレートに渡す
    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('index.html', google_maps_api_key=google_maps_api_key)

@bp.route('/calculate', methods=['POST'])
def calculate():
    try:
        # フォームデータを取得
        birth_date = datetime.strptime(request.form['birthDate'], '%Y-%m-%d').date()
        birth_time = datetime.strptime(request.form['birthTime'], '%H:%M').time()
        birth_place = request.form['birthPlace']
        
        # 緯度経度が手動入力されているか確認
        manual_latitude = request.form.get('latitude')
        manual_longitude = request.form.get('longitude')
        
        # 手動入力された緯度経度を使用
        if manual_latitude and manual_longitude:
            try:
                latitude = float(manual_latitude)
                longitude = float(manual_longitude)
                location_source = '手動入力'
            except ValueError:
                return jsonify({
                    'success': False, 
                    'error': '緯度経度の形式が正しくありません。数値を入力してください。'
                }), 400
        else:
            # 地名から緯度経度を取得
            latitude, longitude, location_found = get_city_coordinates(birth_place)
            
            if location_found:
                location_source = f'地名データベース（{birth_place}）'
            
            # 地名が見つからない場合、Google Maps APIを試す
            if not location_found:
                # APIキーが設定されているか確認し、APIを呼び出す
                api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
                if api_key:
                    google_lat, google_lng, google_found = get_coordinates_from_google_maps(birth_place, api_key)
                    if google_found:
                        latitude = google_lat
                        longitude = google_lng
                        location_found = True
                        location_source = f'Google Maps API（{birth_place}）'
            
            # それでも地名が見つからない場合
            if not location_found:
                # デフォルト値（東京）を使用
                latitude = 35.6895
                longitude = 139.6917
                location_source = 'デフォルト（東京）'
                # フラグを設定して、結果ページでアラートを表示
                location_warning = True
            else:
                location_warning = False
        
        timezone_offset = 9.0 # 日本標準時
        house_system = b'P' # Placidus
        # house_system = b'W' # 仮: Whole Sign に変更して試す

        # ネイタルチャートの計算 (cusps も受け取る)
        natal_positions, chart_info, natal_cusps = calculate_natal_chart(
            birth_date, birth_time, birth_place,
            latitude, longitude, timezone_offset, house_system
        )

        # 月のノード（ドラゴンヘッド/テイル）の計算
        jd_ut = chart_info.get('jd_ut', None)
        
        lunar_nodes = None
        lunar_node_interpretations = {}
        
        if jd_ut:
            # 月のノード計算
            lunar_nodes = calculate_lunar_nodes(jd_ut)
            
            # 月のノードの解釈
            if 'True_Node' in lunar_nodes and 'sign_jp' in lunar_nodes['True_Node']:
                sign_jp = lunar_nodes['True_Node']['sign_jp']
                if sign_jp in NODE_INTERPRETATIONS['True_Node']:
                    lunar_node_interpretations['True_Node'] = NODE_INTERPRETATIONS['True_Node'][sign_jp]
            
            if 'Dragon_Tail' in lunar_nodes and 'sign_jp' in lunar_nodes['Dragon_Tail']:
                sign_jp = lunar_nodes['Dragon_Tail']['sign_jp']
                if sign_jp in NODE_INTERPRETATIONS['Dragon_Tail']:
                    lunar_node_interpretations['Dragon_Tail'] = NODE_INTERPRETATIONS['Dragon_Tail'][sign_jp]
            
            # ネイタルポジションに月のノードを追加
            if lunar_nodes:
                for node_name, node_data in lunar_nodes.items():
                    natal_positions[node_name] = node_data

        # ネイタルアスペクトの計算
        natal_aspects = calculate_aspects(natal_positions) # positions1 のみ渡す

        # アスペクトグリッドの生成
        aspect_grid_data = generate_aspect_grid(natal_aspects)

        # SVGチャートの生成
        chart_svg = generate_chart_svg(natal_positions, natal_cusps, natal_aspects, chart_info) # natal_aspects と chart_info を追加

        # サビアンシンボルの取得 (ASC, MCは対象外とするか？)
        natal_sabian = {}
        for planet, pos in natal_positions.items():
            # ASC, MC はサビアンシンボルの対象外とする場合
            if planet in ['Asc', 'MC']: continue
            # sabian.py が longitude キーを期待しているか確認 -> OK
            sabian_text = get_sabian_symbol(pos['longitude']) # シンボル文を直接取得
            if sabian_text: # sabian_text が None や空でないことを確認
                natal_sabian[planet] = {
                    'symbol': sabian_text,      # シンボル文（例: 牡羊座1度: ...）
                    'interpretation': sabian_text # 解釈文も同じシンボル文とする
                }

        # 解釈文の取得
        interpretations = {
            'planet_in_sign': {},
            'planet_in_house': {},
            'aspects': []
        }

        # 主要な天体リスト (解釈取得用)
        major_planets_for_interp = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']

        # 天体のサイン解釈とハウス解釈を取得
        for planet in major_planets_for_interp:
            if planet in natal_positions:
                planet_data = natal_positions[planet]
                sign_jp = planet_data.get('sign_jp')
                house = planet_data.get('house')
                planet_jp = planet_data.get('name_jp', planet) # 日本語名を取得
                planet_glyph = planet_data.get('glyph') # 記号を取得

                # サイン解釈
                if sign_jp:
                    interp_key = f"{planet_jp} ({sign_jp})"
                    interp_text = PLANET_IN_SIGN_INTERPRETATIONS.get(planet, {}).get(sign_jp, f"{planet_jp}のサイン解釈は準備中です。")
                    interpretations['planet_in_sign'][planet] = {
                        'text': interp_text,
                        'key': interp_key,
                        'glyph': planet_glyph # glyph を追加
                    }

                # ハウス解釈
                if house:
                    interp_key = f"{planet_jp} ({house}ハウス)"
                    # PLANET_IN_HOUSE_INTERPRETATIONS のキーは英語名のまま
                    interp_text = PLANET_IN_HOUSE_INTERPRETATIONS.get(planet, {}).get(house, f"{planet_jp}のハウス解釈は準備中です。")
                    interpretations['planet_in_house'][planet] = {
                        'text': interp_text,
                        'key': interp_key,
                        'glyph': planet_glyph # glyph を追加
                    }

        # ネイタルアスペクトの解釈を取得
        if natal_aspects:
            for aspect in natal_aspects:
                p1 = aspect.get('planet1')
                p2 = aspect.get('planet2')
                p1_jp = aspect.get('planet1_jp', p1) # 日本語名を取得
                p2_jp = aspect.get('planet2_jp', p2) # 日本語名を取得
                aspect_type = aspect.get('aspect_type')
                aspect_glyph = aspect.get('aspect_glyph')
                p1_glyph = aspect.get('planet1_glyph')
                p2_glyph = aspect.get('planet2_glyph')

                if p1 and p2 and aspect_type:
                    planets_sorted = sorted([p1, p2])
                    # aspect_type を小文字に変換してキーを作成
                    interp_key = f"{planets_sorted[0]}_{planets_sorted[1]}_{aspect_type.lower()}"
                    # 解釈文辞書のキーは英語名のまま
                    interp_text = ASPECT_INTERPRETATIONS.get(interp_key, f"{p1_jp} {aspect_glyph} {p2_jp} の解釈は準備中です。")

                    # 主要アスペクトかどうかを判定
                    MAJOR_ASPECT_TYPES = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
                    is_major_aspect = aspect_type.lower() in MAJOR_ASPECT_TYPES

                    interpretations['aspects'].append({
                        'planet1': p1,
                        'planet2': p2,
                        'planet1_jp': p1_jp, # 日本語名を追加
                        'planet2_jp': p2_jp, # 日本語名を追加
                        'aspect_type': aspect_type,
                        'aspect_glyph': aspect_glyph,
                        'planet1_glyph': p1_glyph,
                        'planet2_glyph': p2_glyph,
                        'text': interp_text,
                        'is_major': is_major_aspect # is_major フラグを追加
                    })

        current_app.logger.debug(f"Constructed interpretations: {interpretations}") # ★デバッグログ追加

        # トランジットの計算（指定がある場合）
        transit_positions = None
        transit_aspects = None # トランジットアスペクト用
        transit_sabian = None
        transit_date = None
        transit_aspect_interpretations = [] # トランジットアスペクト解釈用

        if 'transitDate' in request.form and request.form['transitDate']:
            transit_date_str = request.form['transitDate']
            # datetime-local 形式 (%Y-%m-%dT%H:%M) を想定
            transit_date = datetime.strptime(transit_date_str, '%Y-%m-%dT%H:%M')
            transit_positions = calculate_transit(transit_date, birth_date, birth_time, birth_place,
                                                  latitude, longitude, timezone_offset)
            # トランジット-ネイタルアスペクトの計算
            transit_aspects = calculate_aspects(transit_positions, natal_positions)

            # トランジットアスペクトの解釈を取得
            if transit_aspects:
                for aspect in transit_aspects:
                    p1 = aspect.get('planet1') # Transit planet
                    p2 = aspect.get('planet2') # Natal planet
                    p1_jp = aspect.get('planet1_jp', p1)
                    p2_jp = aspect.get('planet2_jp', p2)
                    aspect_type = aspect.get('aspect_type')
                    aspect_glyph = aspect.get('aspect_glyph')
                    p1_glyph = aspect.get('planet1_glyph')
                    p2_glyph = aspect.get('planet2_glyph')

                    if p1 and p2 and aspect_type:
                        # トランジットの場合、p1(T)とp2(N)の順序は固定でソートしないことが多いが、
                        # ASPECT_INTERPRETATIONSのキー構造に合わせる必要がある。
                        # 現状のASPECT_INTERPRETATIONSは英語名ソートなので、それに合わせる。
                        # T.Sun-N.Moon と N.Moon-T.Sun のような区別をしたい場合はキー構造の変更が必要。
                        planets_sorted_for_key = sorted([p1, p2]) # キー検索用にソート
                        # aspect_type を小文字に変換してキーを作成
                        interp_key = f"{planets_sorted_for_key[0]}_{planets_sorted_for_key[1]}_{aspect_type.lower()}"
                        interp_text = ASPECT_INTERPRETATIONS.get(interp_key, f"T.{p1_jp} {aspect_glyph} N.{p2_jp} の解釈は準備中です。")
                        
                        # 主要アスペクトかどうかを判定
                        MAJOR_ASPECT_TYPES = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
                        is_major_aspect = aspect_type.lower() in MAJOR_ASPECT_TYPES
                        
                        transit_aspect_interpretations.append({
                            'planet1': p1, 'planet2': p2,
                            'planet1_jp': p1_jp, 'planet2_jp': p2_jp,
                            'aspect_type': aspect_type,
                            'aspect_glyph': aspect_glyph,
                            'planet1_glyph': p1_glyph, 'planet2_glyph': p2_glyph,
                            'orb': aspect.get('orb'), # オーブも追加
                            'text': interp_text,
                            'is_major': is_major_aspect # is_major フラグを追加
                        })

            # トランジットのサビアンシンボル
            transit_sabian = {}
            for planet, pos in transit_positions.items():
                 sabian_text = get_sabian_symbol(pos['longitude']) # シンボル文を直接取得
                 if sabian_text: # sabian_text が None や空でないことを確認
                     transit_sabian[planet] = {
                         'symbol': sabian_text,      # シンボル文
                         'interpretation': sabian_text # 解釈文も同じシンボル文
                     }

        # ソーラーアーク予測
        solar_arc_forecast = calculate_solar_arc_sabian_forecast(
            birth_date, birth_time, birth_place,
            latitude, longitude, timezone_offset
        )

        # 進行法計算年数の取得（デフォルトは3年）
        progression_years = 3
        if 'progression_years' in request.form and request.form['progression_years']:
            try:
                progression_years = int(request.form['progression_years'])
            except ValueError:
                # 整数に変換できない場合はデフォルト値を使用
                pass

        # ソーラーアーク予測（更新）
        solar_arc_forecast = calculate_solar_arc_sabian_forecast(
            birth_date, birth_time, birth_place,
            latitude, longitude, timezone_offset,
            years_to_forecast=progression_years
        )

        # 二次進行法による予測
        secondary_progression = calculate_secondary_progression(
            birth_date, birth_time, birth_place,
            latitude, longitude, timezone_offset,
            years_to_forecast=progression_years
        )

        # 春分点のサビアンシンボル (ネイタル年)
        vernal_equinox_sabian = calculate_vernal_equinox_sabian(birth_date.year)

        # 夏至点のサビアンシンボル (ネイタル年)
        summer_solstice_sabian = calculate_summer_solstice_sabian(birth_date.year)

        # 秋分点のサビアンシンボル (ネイタル年)
        autumnal_equinox_sabian = calculate_autumnal_equinox_sabian(birth_date.year)

        # 冬至点のサビアンシンボル (ネイタル年)
        winter_solstice_sabian = calculate_winter_solstice_sabian(birth_date.year)

        # --- 年間イベントのサビアンシンボル計算 (現在の年を使用) ---
        current_year = datetime.now().year
        # solar_arc_forecast の再計算は、必要に応じて行う。ここでは natal_positions を使った初期計算を流用。
        # solar_arc_forecast = calculate_solar_arc_sabian_forecast(
        #     birth_date, birth_time, birth_place,
        #     latitude, longitude, timezone_offset
        # )
        vernal_equinox_sabian_current = calculate_vernal_equinox_sabian(current_year)
        summer_solstice_sabian_current = calculate_summer_solstice_sabian(current_year)
        autumnal_equinox_sabian_current = calculate_autumnal_equinox_sabian(current_year)
        winter_solstice_sabian_current = calculate_winter_solstice_sabian(current_year)
        # --- ここまで年間イベント計算 ---

        # equinox_data の定義 (テンプレートで使用)
        equinox_data = {
            'vernal': vernal_equinox_sabian_current,
            'summer': summer_solstice_sabian_current,
            'autumnal': autumnal_equinox_sabian_current,
            'winter': winter_solstice_sabian_current,
            'year': current_year
        }

        # ライフイベント予測の生成
        forecast_years = int(request.form.get('forecast_years', 3))
        life_events = predict_life_events(natal_positions, forecast_years)

        # PDFの生成（結果データに含める前に生成）
        # PDF生成関数に渡すデータ構造を一時的に作成
        pdf_result_data = {
            'birth_date': birth_date.strftime('%Y-%m-%d'),
            'birth_time': birth_time.strftime('%H:%M'),
            'birth_place': birth_place,
            'natal': {
                'positions': natal_positions,
                'aspects': natal_aspects,
                'sabian': natal_sabian,
                'latitude': latitude,
                'longitude': longitude,
                'location_source': location_source,
                'location_warning': location_warning if 'location_warning' in locals() else False,
                **chart_info
            },
            'aspect_grid': aspect_grid_data,
            'chart_svg': chart_svg, 
            'interpretations': interpretations,
            'solar_arc_forecast': solar_arc_forecast, # PDFに追加
            'secondary_progression': secondary_progression, # 二次進行法のデータを追加
            'vernal_equinox_sabian': vernal_equinox_sabian, # PDFに追加
            'summer_solstice_sabian': summer_solstice_sabian, # PDFに追加
            'autumnal_equinox_sabian': autumnal_equinox_sabian, # PDFに追加
            'winter_solstice_sabian': winter_solstice_sabian, # PDFに追加
            'current_year_for_seasonal': current_year, # PDFに年も渡す (キー名を変更)
            'forecast_years': forecast_years,
            'life_events': life_events
        }
        if transit_positions:
            pdf_result_data['transit'] = {
                'positions': transit_positions,
                'aspects': transit_aspects, 
                'aspect_interpretations': transit_aspect_interpretations, 
                'sabian': transit_sabian
            }
            pdf_result_data['transit_date'] = transit_date.strftime('%Y-%m-%d %H:%M')

        pdf_filename = generate_horoscope_pdf(pdf_result_data) # PDF生成実行
        pdf_url = url_for('static', filename=f'pdfs/{pdf_filename}')

        # テンプレートに変数を渡して結果ページをレンダリング
        result_data_for_template = {
            'birth_date': birth_date.strftime('%Y-%m-%d'), # 文字列に変換
            'birth_time': birth_time.strftime('%H:%M'), # 文字列に変換
            'birth_place': birth_place,
            'location_source': location_source,
            'location_warning': location_warning if 'location_warning' in locals() else False,
            'natal': { # ネイタル情報を 'natal' キーの下にまとめる
                'positions': natal_positions,
                'latitude': latitude,
                'longitude': longitude,
                'chart_info': chart_info,
                'sabian': natal_sabian if 'natal_sabian' in locals() else None,
                'aspects': natal_aspects,
                'lunar_nodes': lunar_nodes, # 月のノードも natal に含めるか検討 (PDF構造に合わせるか)
                'lunar_node_interpretations': lunar_node_interpretations # 同上
            },
            'interpretations': interpretations if 'interpretations' in locals() else None,
            'aspect_grid': aspect_grid_data, # aspect_gridを'natal'キーの外に移動
            'transit': { # トランジット情報も 'transit' キーの下にまとめる
                'positions': transit_positions if 'transit_positions' in locals() else None,
                'date_str': transit_date.strftime('%Y-%m-%d %H:%M') if transit_date else None, # transit_date を文字列に
                'aspects': transit_aspects if 'transit_aspects' in locals() else None,
                'sabian': transit_sabian if 'transit_sabian' in locals() else None,
                'aspect_interpretations': transit_aspect_interpretations if 'transit_aspect_interpretations' in locals() else None,
            },
            'chart_svg': chart_svg, # chart_svg は natal の外のままにするか検討 (result.html の現状に合わせる)
            'progression_data': secondary_progression if 'secondary_progression' in locals() else None,
            'equinox_data': equinox_data,
            'life_events': life_events,
            'forecast_years': forecast_years,
            'pdf_url': pdf_url
        }

        current_app.logger.debug(f"Data passed to template result: {result_data_for_template['natal']['interpretations']}") # ★デバッグログ追加

        return render_template('result.html', result=result_data_for_template)
    except Exception as e:
        current_app.logger.error(f"Error in /calculate: ExceptionType={type(e).__name__}, ErrorMessage={repr(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/synastry', methods=['GET'])
def synastry_form():
    """相性占い（シナストリー）入力フォームの表示"""
    # 現在時刻を取得（トランジット日時のデフォルト値として使用）
    now = datetime.now()
    today_datetime = now.strftime('%Y-%m-%dT%H:%M')

    # Google Maps APIキーをテンプレートに渡す
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')

    return render_template('synastry_form.html', 
                          today_datetime=today_datetime,
                          google_maps_api_key=google_maps_api_key)

@bp.route('/calculate_synastry', methods=['POST'])
def calculate_synastry():
    """相性占い（シナストリー）の計算実行"""
    try:
        # 人物1の入力情報
        birth_date1 = datetime.strptime(request.form['birthDate1'], '%Y-%m-%d').date()
        birth_time1 = datetime.strptime(request.form['birthTime1'], '%H:%M').time()
        birth_place1 = request.form['birthPlace1']
        
        # 人物2の入力情報
        birth_date2 = datetime.strptime(request.form['birthDate2'], '%Y-%m-%d').date()
        birth_time2 = datetime.strptime(request.form['birthTime2'], '%H:%M').time()
        birth_place2 = request.form['birthPlace2']
        
        # 緯度経度の取得（人物1）
        latitude1 = float(request.form.get('latitude1', 35.6895))
        longitude1 = float(request.form.get('longitude1', 139.6917))
        location_source1 = request.form.get('location_source1', 'デフォルト（東京）')
        location_warning1 = request.form.get('location_warning1', 'True') == 'True'
        
        # 緯度経度の取得（人物2）
        latitude2 = float(request.form.get('latitude2', 35.6895))
        longitude2 = float(request.form.get('longitude2', 139.6917))
        location_source2 = request.form.get('location_source2', 'デフォルト（東京）')
        location_warning2 = request.form.get('location_warning2', 'True') == 'True'
        
        # タイムゾーンオフセットを計算（人物1と人物2）
        timezone_offset1 = 9.0 # 仮の値
        timezone_offset2 = 9.0 # 仮の値
        
        # ホロスコープ計算（人物1）
        natal_positions1, chart_info1_returned, natal_cusps1 = calculate_natal_chart(
            birth_date1, birth_time1, birth_place1, latitude1, longitude1, timezone_offset1, house_system=b'P'
        )
        chart_info1 = chart_info1_returned.copy()
        chart_info1['house_cusps'] = natal_cusps1
        for planet_name, pos_data in natal_positions1.items():
            pos_data['house'] = get_house_number(pos_data['longitude'], chart_info1['house_cusps'])
        
        # ネイタルアスペクトの計算（人物1）
        natal_aspects1 = calculate_aspects(natal_positions1)

        # ホロスコープ計算（人物2）
        natal_positions2, chart_info2_returned, natal_cusps2 = calculate_natal_chart(
            birth_date2, birth_time2, birth_place2, latitude2, longitude2, timezone_offset2, house_system=b'P'
        )
        chart_info2 = chart_info2_returned.copy()
        chart_info2['house_cusps'] = natal_cusps2
        for planet_name, pos_data in natal_positions2.items():
            pos_data['house'] = get_house_number(pos_data['longitude'], chart_info2['house_cusps'])
            
        # ネイタルアスペクトの計算（人物2）
        natal_aspects2 = calculate_aspects(natal_positions2)

        # アスペクトグリッドの生成（人物1と人物2）
        aspect_grid_data1 = generate_aspect_grid(natal_aspects1, list(natal_positions1.keys()))
        aspect_grid_data2 = generate_aspect_grid(natal_aspects2, list(natal_positions2.keys()))

        # チャート画像（SVG）の生成（人物1と人物2）
        chart_svg1 = generate_chart_svg(natal_positions1, chart_info1['house_cusps'], natal_aspects1, chart_info1)
        chart_svg2 = generate_chart_svg(natal_positions2, chart_info2['house_cusps'], natal_aspects2, chart_info2)

        # サビアンシンボルの取得（人物1と人物2）
        natal_sabian1 = {}
        for planet, pos in natal_positions1.items():
            sabian_text = get_sabian_symbol(pos['longitude'])
            if sabian_text:
                natal_sabian1[planet] = {
                    'symbol': sabian_text,
                    'interpretation': sabian_text
                }

        natal_sabian2 = {}
        for planet, pos in natal_positions2.items():
            sabian_text = get_sabian_symbol(pos['longitude'])
            if sabian_text:
                natal_sabian2[planet] = {
                    'symbol': sabian_text,
                    'interpretation': sabian_text
                }

        # 人物1の情報を辞書にまとめる
        person1_data = {
            'positions': natal_positions1,
            'aspects': natal_aspects1,
            'sabian': natal_sabian1,
            'latitude': latitude1,
            'longitude': longitude1,
            'timezone_offset': timezone_offset1,
            **chart_info1
        }

        # 人物2の情報を辞書にまとめる
        person2_data = {
            'positions': natal_positions2,
            'aspects': natal_aspects2,
            'sabian': natal_sabian2,
            'latitude': latitude2,
            'longitude': longitude2,
            'timezone_offset': timezone_offset2,
            **chart_info2
        }

        # シナストリー計算
        synastry_data = hs_calculate_synastry(person1_data, person2_data)

        # シナストリーアスペクト解釈を取得
        synastry_aspect_interpretations = []
        if synastry_data['synastry_aspects']:
            for aspect in synastry_data['synastry_aspects']:
                p1 = aspect.get('person1_planet')
                p2 = aspect.get('person2_planet')
                p1_jp = aspect.get('person1_planet_jp', p1)
                p2_jp = aspect.get('person2_planet_jp', p2)
                aspect_type = aspect.get('aspect_type')
                aspect_glyph = aspect.get('aspect_glyph')
                p1_glyph = aspect.get('person1_planet_glyph')
                p2_glyph = aspect.get('person2_planet_glyph')

                if p1 and p2 and aspect_type:
                    # シナストリーアスペクト解釈のキーを作成（順序考慮）
                    interp_key = f"{p1}_{p2}_{aspect_type.lower()}_synastry"
                    # interp_text = get_interpretation_text(interp_key, f"{p1_jp} - {p2_jp}（{aspect_type}）") # 古い呼び出しをコメントアウト
                    interp_text = ASPECT_INTERPRETATIONS.get(interp_key, f"{p1_jp} - {p2_jp}（{aspect_type}）の解釈は準備中です。") # ASPECT_INTERPRETATIONS から直接取得
                    
                    # 主要アスペクトかどうかを判定
                    MAJOR_ASPECT_TYPES = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
                    is_major_aspect = aspect_type.lower() in MAJOR_ASPECT_TYPES
                    
                    synastry_aspect_interpretations.append({
                        'person1_planet': p1, 'person2_planet': p2,
                        'person1_planet_jp': p1_jp, 'person2_planet_jp': p2_jp,
                        'aspect_type': aspect_type,
                        'aspect_glyph': aspect_glyph,
                        'person1_planet_glyph': p1_glyph, 'person2_planet_glyph': p2_glyph,
                        'orb': aspect.get('orb'), # オーブも追加
                        'text': interp_text,
                        'is_major': is_major_aspect # is_major フラグを追加
                    })

        # 合成図のチャート生成
        composite_chart_svg = generate_chart_svg(synastry_data['composite_positions'], chart_info1['house_cusps'], synastry_data['composite_aspects'], {'house_system': 'Placidus'})

        # 相性度（単純なスコア）の計算
        # ハードアスペクト（60点）、ソフトアスペクト（40点）で計算
        compatibility_score = 50 # 基本点数を50点とする
        max_score = 100
        min_score = 0
        
        # IMPORTANT_PLANETS_FOR_SYNASTRY = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Asc', 'MC'] # 修正案１：対象天体を限定
        # 対象天体リスト（より相性で重視されるもの）
        PRIMARY_TARGETS = ['Sun', 'Moon', 'Venus', 'Mars', 'Asc', 'MC']
        SECONDARY_TARGETS = ['Mercury', 'Jupiter', 'Saturn']

        for aspect in synastry_data['synastry_aspects']:
            p1 = aspect.get('person1_planet')
            p2 = aspect.get('person2_planet')
            aspect_type = aspect.get('aspect_type')
            orb = aspect.get('orb', 5) # オーブが取得できない場合はデフォルト5度とする

            # 両方の天体が評価対象に含まれるか、または主要天体同士か
            is_primary_aspect = (p1 in PRIMARY_TARGETS and p2 in PRIMARY_TARGETS)
            # is_secondary_aspect = (p1 in PRIMARY_TARGETS and p2 in SECONDARY_TARGETS) or \
            #                       (p1 in SECONDARY_TARGETS and p2 in PRIMARY_TARGETS)

            # 主要天体同士のアスペクトを重視
            point_modifier = 1.0
            if is_primary_aspect:
                point_modifier = 1.2 # 主要天体同士は1.2倍の重み (前回1.5倍)

            # オーブによる調整 (タイトなほど影響大)
            orb_modifier = 1.0
            if orb <= 2: # オーブ2度以下は影響大
                orb_modifier = 1.1 # 前回1.2倍
            elif orb > 5: # オーブ5度より大きい場合は影響小
                orb_modifier = 0.9 # 前回0.8倍

            base_point = 0
            if aspect_type == 'Conjunction':
                if (p1 in ['Sun', 'Moon', 'Venus', 'Mars'] and p2 in ['Sun', 'Moon', 'Venus', 'Mars']):
                    base_point = 15 # 前回20点
                else:
                    base_point = 10 # 前回15点
            elif aspect_type == 'Trine' or aspect_type == 'Sextile':
                base_point = 7  # 前回10点
            elif aspect_type == 'Square' or aspect_type == 'Opposition':
                base_point = -12 # 前回-10点 (減点幅をさらに大きく)
            
            compatibility_score += base_point * point_modifier * orb_modifier
        
        # スコアを0-100の範囲に収める
        compatibility_score = max(min_score, min(compatibility_score, max_score))
        compatibility_score = round(compatibility_score) # 整数に丸める

        # 結果データの作成
        result_data = {
            'person1': {
                'birth_date': birth_date1.strftime('%Y-%m-%d'),
                'birth_time': birth_time1.strftime('%H:%M'),
                'birth_place': birth_place1,
                'natal': {
                    'positions': natal_positions1,
                    'aspects': natal_aspects1,
                    'sabian': natal_sabian1,
                    'latitude': latitude1,
                    'longitude': longitude1,
                    'location_source': location_source1,
                    'location_warning': location_warning1,
                    **chart_info1
                },
                'aspect_grid': aspect_grid_data1,
                'chart_svg': chart_svg1
            },
            'person2': {
                'birth_date': birth_date2.strftime('%Y-%m-%d'),
                'birth_time': birth_time2.strftime('%H:%M'),
                'birth_place': birth_place2,
                'natal': {
                    'positions': natal_positions2,
                    'aspects': natal_aspects2,
                    'sabian': natal_sabian2,
                    'latitude': latitude2,
                    'longitude': longitude2,
                    'location_source': location_source2,
                    'location_warning': location_warning2,
                    **chart_info2
                },
                'aspect_grid': aspect_grid_data2,
                'chart_svg': chart_svg2
            },
            'synastry': {
                'aspects': synastry_data['synastry_aspects'],
                'aspect_interpretations': synastry_aspect_interpretations,
                'composite_positions': synastry_data['composite_positions'],
                'composite_aspects': synastry_data['composite_aspects'],
                'composite_chart_svg': composite_chart_svg,
                'compatibility_score': compatibility_score
            }
        }
        
        # PDF生成
        # PDFに渡すデータはHTML用とほぼ同じだが、SVGは含めない、または別途処理を検討
        pdf_data = result_data.copy() # PDF用のデータを準備（必要に応じて調整）
        # 例えば、SVGはPDFでは扱いが異なる場合があるので、PDFデータからは除外したり、画像に変換するなどの処理が必要な場合がある
        # ここでは簡単のためHTMLと同じデータ構造を渡すが、synastry_pdf.html側でSVGを適切に扱えない場合は調整が必要
        
        pdf_filename = generate_synastry_pdf(pdf_data) 
        pdf_url = url_for('static', filename=f'pdfs/{pdf_filename}')
        result_data['pdf_url'] = pdf_url # HTMLテンプレートにPDFのURLを渡す
        
        return render_template('synastry_result.html', result=result_data)
        
    except Exception as e:
        current_app.logger.error(f"Error in /calculate_synastry: {e}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 新しいエンドポイント: 月のノード専用ページ
@bp.route('/lunar_nodes', methods=['GET'])
def lunar_nodes_form():
    """月のノード（ドラゴンヘッド/テイル）計算フォームを表示"""
    # Google Maps APIキーをテンプレートに渡す
    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('lunar_nodes_form.html', google_maps_api_key=google_maps_api_key)

@bp.route('/calculate_lunar_nodes', methods=['POST'])
def calculate_lunar_nodes_endpoint():
    """月のノード（ドラゴンヘッド/テイル）の計算と解釈を行う"""
    try:
        # フォームデータを取得 (HTMLのname属性に合わせる)
        birth_date = datetime.strptime(request.form['birthDate'], '%Y-%m-%d').date()
        birth_time = datetime.strptime(request.form['birthTime'], '%H:%M').time()
        birth_place = request.form['birthPlace']
        
        # 緯度経度が手動入力されているか確認
        manual_latitude = request.form.get('latitude')
        manual_longitude = request.form.get('longitude')
        
        # 手動入力された緯度経度を使用
        if manual_latitude and manual_longitude:
            try:
                latitude = float(manual_latitude)
                longitude = float(manual_longitude)
                location_source = '手動入力'
            except ValueError:
                return jsonify({
                    'success': False, 
                    'error': '緯度経度の形式が正しくありません。数値を入力してください。'
                }), 400
        else:
            # 地名から緯度経度を取得
            latitude, longitude, location_found = get_city_coordinates(birth_place)
            
            if location_found:
                location_source = f'地名データベース（{birth_place}）'
            
            # 地名が見つからない場合、Google Maps APIを試す
            if not location_found:
                # APIキーが設定されているか確認し、APIを呼び出す
                api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
                if api_key:
                    google_lat, google_lng, google_found = get_coordinates_from_google_maps(birth_place, api_key)
                    if google_found:
                        latitude = google_lat
                        longitude = google_lng
                        location_found = True
                        location_source = f'Google Maps API（{birth_place}）'
            
            # それでも地名が見つからない場合
            if not location_found:
                # デフォルト値（東京）を使用
                latitude = 35.6895
                longitude = 139.6917
                location_source = 'デフォルト（東京）'
                # フラグを設定して、結果ページでアラートを表示
                location_warning = True
            else:
                location_warning = False
        
        timezone_offset = 9.0 # 日本標準時
        
        # 出生時のユリウス日を計算
        dt_naive = datetime.combine(birth_date, birth_time)
        tz = timezone(timedelta(hours=timezone_offset))
        dt_aware = dt_naive.replace(tzinfo=tz)
        dt_utc = dt_aware.astimezone(timezone.utc)
        jd_ut = swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day,
                            dt_utc.hour, dt_utc.minute, dt_utc.second, 1)[1]
        
        # 月のノードを計算
        lunar_nodes = calculate_lunar_nodes(jd_ut)
        
        # 月のノードの解釈
        lunar_node_interpretations = {}
        
        if 'True_Node' in lunar_nodes and 'sign_jp' in lunar_nodes['True_Node']:
            sign_jp = lunar_nodes['True_Node']['sign_jp']
            if sign_jp in NODE_INTERPRETATIONS['True_Node']:
                lunar_node_interpretations['True_Node'] = NODE_INTERPRETATIONS['True_Node'][sign_jp]
        
        if 'Dragon_Tail' in lunar_nodes and 'sign_jp' in lunar_nodes['Dragon_Tail']:
            sign_jp = lunar_nodes['Dragon_Tail']['sign_jp']
            if sign_jp in NODE_INTERPRETATIONS['Dragon_Tail']:
                lunar_node_interpretations['Dragon_Tail'] = NODE_INTERPRETATIONS['Dragon_Tail'][sign_jp]
        
        # PDF生成用のデータを準備
        pdf_data = {
            'birth_date': birth_date.strftime('%Y-%m-%d'),
            'birth_time': birth_time.strftime('%H:%M'),
            'birth_place': birth_place,
            'latitude': latitude,
            'longitude': longitude,
            'location_source': location_source,
            'location_warning': location_warning if 'location_warning' in locals() else False,
            'lunar_nodes': lunar_nodes,
            'lunar_node_interpretations': lunar_node_interpretations
        }
        
        # PDF生成
        pdf_filename = generate_lunar_nodes_pdf(pdf_data)
        pdf_url = url_for('static', filename=f'pdfs/{pdf_filename}')
        
        # 結果ページへのリダイレクト用URLを生成
        result_url = url_for('main.lunar_nodes_result', 
                            birth_date=birth_date.strftime('%Y-%m-%d'),
                            birth_time=birth_time.strftime('%H:%M'),
                            birth_place=birth_place,
                            latitude=latitude,
                            longitude=longitude,
                            location_source=location_source,
                            location_warning=location_warning if 'location_warning' in locals() else False,
                            pdf_url=pdf_url)
        
        # クライアントにJSONでリダイレクト先URLを返す
        return jsonify({
            'success': True,
            'redirect_url': result_url
        })
    except Exception as e:
        current_app.logger.error(f"Error in /calculate_lunar_nodes: {e}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/lunar_nodes_result', methods=['GET'])
def lunar_nodes_result():
    """月のノード計算結果ページをレンダリングする"""
    try:
        # URLパラメータから情報を取得
        birth_date = request.args.get('birth_date')
        birth_time = request.args.get('birth_time')
        birth_place = request.args.get('birth_place')
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        location_source = request.args.get('location_source')
        location_warning = request.args.get('location_warning') == 'True'
        pdf_url = request.args.get('pdf_url')
        
        # 出生情報からデータを再計算（または計算済みのデータをセッションから取得するなど）
        birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
        birth_time_obj = datetime.strptime(birth_time, '%H:%M').time()
        
        timezone_offset = 9.0  # 日本標準時
        dt_naive = datetime.combine(birth_date_obj, birth_time_obj)
        tz = timezone(timedelta(hours=timezone_offset))
        dt_aware = dt_naive.replace(tzinfo=tz)
        dt_utc = dt_aware.astimezone(timezone.utc)
        jd_ut = swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day,
                            dt_utc.hour, dt_utc.minute, dt_utc.second, 1)[1]
        
        # 月のノードを計算
        lunar_nodes = calculate_lunar_nodes(jd_ut)
        
        # 月のノードの解釈
        lunar_node_interpretations = {}
        
        if 'True_Node' in lunar_nodes and 'sign_jp' in lunar_nodes['True_Node']:
            sign_jp = lunar_nodes['True_Node']['sign_jp']
            if sign_jp in NODE_INTERPRETATIONS['True_Node']:
                lunar_node_interpretations['True_Node'] = NODE_INTERPRETATIONS['True_Node'][sign_jp]
        
        if 'Dragon_Tail' in lunar_nodes and 'sign_jp' in lunar_nodes['Dragon_Tail']:
            sign_jp = lunar_nodes['Dragon_Tail']['sign_jp']
            if sign_jp in NODE_INTERPRETATIONS['Dragon_Tail']:
                lunar_node_interpretations['Dragon_Tail'] = NODE_INTERPRETATIONS['Dragon_Tail'][sign_jp]
        
        # テンプレートに変数を渡して結果ページをレンダリング
        return render_template('lunar_nodes_result.html', 
                              birth_date=birth_date_obj,
                              birth_time=birth_time_obj,
                              birth_place=birth_place,
                              latitude=latitude,
                              longitude=longitude,
                              location_source=location_source,
                              location_warning=location_warning,
                              lunar_nodes=lunar_nodes,
                              lunar_node_interpretations=lunar_node_interpretations,
                              pdf_url=pdf_url)
    except Exception as e:
        current_app.logger.error(f"Error in /lunar_nodes_result: {e}\n{traceback.format_exc()}")
        return render_template('error.html', error=str(e))

# 新しいエンドポイント: ライフイベント予測専用ページ
@bp.route('/life_events', methods=['GET'])
def life_events_form():
    """ライフイベント予測フォームを表示"""
    # Google Maps APIキーをテンプレートに渡す
    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('life_events_form.html', google_maps_api_key=google_maps_api_key)

@bp.route('/predict_life_events', methods=['POST'])
def predict_life_events_endpoint():
    """ライフイベント予測を行う"""
    try:
        # フォームデータを取得 (HTMLのname属性に合わせる)
        birth_date = datetime.strptime(request.form['birthDate'], '%Y-%m-%d').date()
        birth_time = datetime.strptime(request.form['birthTime'], '%H:%M').time()
        birth_place = request.form['birthPlace']
        forecast_years = int(request.form.get('event_duration_years', 5)) # HTMLのname属性に合わせる
        
        # 緯度経度が手動入力されているか確認
        manual_latitude = request.form.get('latitude')
        manual_longitude = request.form.get('longitude')
        
        # 手動入力された緯度経度を使用
        if manual_latitude and manual_longitude:
            try:
                latitude = float(manual_latitude)
                longitude = float(manual_longitude)
                location_source = '手動入力'
            except ValueError:
                return jsonify({
                    'success': False, 
                    'error': '緯度経度の形式が正しくありません。数値を入力してください。'
                }), 400
        else:
            # 地名から緯度経度を取得
            latitude, longitude, location_found = get_city_coordinates(birth_place)
            
            if location_found:
                location_source = f'地名データベース（{birth_place}）'
            
            # 地名が見つからない場合、Google Maps APIを試す
            if not location_found:
                # APIキーが設定されているか確認し、APIを呼び出す
                api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
                if api_key:
                    google_lat, google_lng, google_found = get_coordinates_from_google_maps(birth_place, api_key)
                    if google_found:
                        latitude = google_lat
                        longitude = google_lng
                        location_found = True
                        location_source = f'Google Maps API（{birth_place}）'
            
            # それでも地名が見つからない場合
            if not location_found:
                # デフォルト値（東京）を使用
                latitude = 35.6895
                longitude = 139.6917
                location_source = 'デフォルト（東京）'
                # フラグを設定して、結果ページでアラートを表示
                location_warning = True
            else:
                location_warning = False
        
        timezone_offset = 9.0 # 日本標準時
        house_system = b'P' # Placidus
        
        # ネイタルチャートの計算
        natal_positions, chart_info, natal_cusps = calculate_natal_chart(
            birth_date, birth_time, birth_place,
            latitude, longitude, timezone_offset, house_system
        )
        
        # ライフイベント予測
        life_events = predict_life_events(natal_positions, forecast_years)
        
        # PDF生成用のデータを準備
        pdf_data = {
            'birth_date': birth_date.strftime('%Y-%m-%d'),
            'birth_time': birth_time.strftime('%H:%M'),
            'birth_place': birth_place,
            'latitude': latitude,
            'longitude': longitude,
            'location_source': location_source,
            'location_warning': location_warning if 'location_warning' in locals() else False,
            'forecast_years': forecast_years,
            'life_events': life_events
        }
        
        # PDF生成
        pdf_filename = generate_life_events_pdf(pdf_data)
        pdf_url = url_for('static', filename=f'pdfs/{pdf_filename}')
        
        # 結果ページへのリダイレクト用URLを生成
        result_url = url_for('main.life_events_result', 
                            birth_date=birth_date.strftime('%Y-%m-%d'),
                            birth_time=birth_time.strftime('%H:%M'),
                            birth_place=birth_place,
                            latitude=latitude,
                            longitude=longitude,
                            location_source=location_source,
                            location_warning=location_warning if 'location_warning' in locals() else False,
                            forecast_years=forecast_years,
                            pdf_url=pdf_url)
        
        # クライアントにJSONでリダイレクト先URLを返す
        return jsonify({
            'success': True,
            'redirect_url': result_url
        })
    except Exception as e:
        current_app.logger.error(f"Error in /predict_life_events: {e}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/life_events_result', methods=['GET'])
def life_events_result():
    """ライフイベント予測結果ページをレンダリングする"""
    try:
        # URLパラメータから情報を取得
        birth_date = request.args.get('birth_date')
        birth_time = request.args.get('birth_time')
        birth_place = request.args.get('birth_place')
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        location_source = request.args.get('location_source')
        location_warning = request.args.get('location_warning') == 'True'
        forecast_years = int(request.args.get('forecast_years', 5))
        pdf_url = request.args.get('pdf_url')
        
        # 出生情報からデータを再計算（または計算済みのデータをセッションから取得するなど）
        birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
        birth_time_obj = datetime.strptime(birth_time, '%H:%M').time()
        
        timezone_offset = 9.0  # 日本標準時
        house_system = b'P'  # Placidus
        
        # ネイタルチャートの計算
        natal_positions, chart_info, natal_cusps = calculate_natal_chart(
            birth_date_obj, birth_time_obj, birth_place,
            latitude, longitude, timezone_offset, house_system
        )
        
        # ライフイベント予測
        life_events = predict_life_events(natal_positions, forecast_years)
        
        # テンプレートに変数を渡して結果ページをレンダリング
        return render_template('life_events_result.html', 
                              birth_date=birth_date_obj,
                              birth_time=birth_time_obj,
                              birth_place=birth_place,
                              latitude=latitude,
                              longitude=longitude,
                              location_source=location_source,
                              location_warning=location_warning,
                              forecast_years=forecast_years,
                              life_events=life_events,
                              pdf_url=pdf_url)
    except Exception as e:
        current_app.logger.error(f"Error in /life_events_result: {e}\n{traceback.format_exc()}")
        return render_template('error.html', error=str(e)) 