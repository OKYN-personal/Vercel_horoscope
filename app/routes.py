from flask import Blueprint, render_template, request, jsonify, url_for, current_app
from datetime import datetime
# from .utils.horoscope import calculate_planet_positions, get_sabian_symbol
# from .utils.aspects import calculate_aspects, get_aspect_description
# from app import create_app # create_appは循環参照になる可能性があるので通常routesからは呼ばない
from app.horoscope import calculate_natal_chart, calculate_transit, calculate_aspects, generate_aspect_grid, \
    calculate_solar_arc_sabian_forecast, calculate_vernal_equinox_sabian, \
    calculate_summer_solstice_sabian, calculate_autumnal_equinox_sabian, calculate_winter_solstice_sabian # 新しい関数をインポート
from app.sabian import get_sabian_symbol # get_interpretation は削除されたのでインポートしない
from app.pdf_generator import generate_horoscope_pdf
from app.chart_generator import generate_chart_svg # SVG生成関数をインポート
from app.interpretations import PLANET_IN_SIGN_INTERPRETATIONS, PLANET_IN_HOUSE_INTERPRETATIONS, ASPECT_INTERPRETATIONS # ハウスとアスペクトの解釈もインポート
from app.utils import get_city_coordinates # 都市座標を取得する関数をインポート
from app.geocoding import get_coordinates_from_google_maps # Google Maps APIを使う関数をインポート

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
        solar_arc_forecast = calculate_solar_arc_sabian_forecast(
            birth_date, birth_time, birth_place,
            latitude, longitude, timezone_offset
        )
        vernal_equinox_sabian = calculate_vernal_equinox_sabian(current_year)
        summer_solstice_sabian = calculate_summer_solstice_sabian(current_year)
        autumnal_equinox_sabian = calculate_autumnal_equinox_sabian(current_year)
        winter_solstice_sabian = calculate_winter_solstice_sabian(current_year)
        # --- ここまで年間イベント計算 ---

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
            'vernal_equinox_sabian': vernal_equinox_sabian, # PDFに追加
            'summer_solstice_sabian': summer_solstice_sabian, # PDFに追加
            'autumnal_equinox_sabian': autumnal_equinox_sabian, # PDFに追加
            'winter_solstice_sabian': winter_solstice_sabian, # PDFに追加
            'current_year_for_seasonal': current_year # PDFに年も渡す (キー名を変更)
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

        # テンプレートに渡す結果データの作成
        result_data = {
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
            'pdf_url': pdf_url, 
            'interpretations': interpretations, 
            'solar_arc_forecast': solar_arc_forecast, 
            'vernal_equinox_sabian': vernal_equinox_sabian, 
            'summer_solstice_sabian': summer_solstice_sabian, 
            'autumnal_equinox_sabian': autumnal_equinox_sabian, 
            'winter_solstice_sabian': winter_solstice_sabian, 
            'current_year_for_seasonal': current_year # HTMLに年も渡す (キー名を変更)
        }
        
        if transit_positions:
            result_data['transit'] = {
                'positions': transit_positions,
                'aspects': transit_aspects, 
                'aspect_interpretations': transit_aspect_interpretations, 
                'sabian': transit_sabian
            }
            result_data['transit_date'] = transit_date.strftime('%Y-%m-%d %H:%M')
        
        # HTMLをレンダリングして返す
        return render_template('result.html', result=result_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc() # エラー詳細をコンソールに表示
        # エラー時はエラーページを表示するか、JSONで返すか選択
        # ここでは例としてJSONでエラーを返す
        return jsonify({'success': False, 'error': str(e)}), 400 