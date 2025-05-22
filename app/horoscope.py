import swisseph as swe
from datetime import datetime, timezone, timedelta
import math
import pytz # タイムゾーン処理に必要
from timezonefinder import TimezoneFinder # 緯度経度からタイムゾーンIDを取得
from .utils import signs, aspect_types, get_sign_jp, get_aspect_glyph, get_planet_glyph # 日本語サイン名取得関数などをインポート
from app.sabian import get_sabian_symbol # ★sabian.pyからget_sabian_symbolをインポート
import logging # ロギング用に追加

# loggingの設定 (必要に応じて設定変更)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 定数
PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
    'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO,
    'True_Node': swe.TRUE_NODE, 'Mean_Node': swe.MEAN_NODE  # 月のノード追加
}
POINTS = {'Asc': 0, 'MC': 1} # swe.houses_ex() の戻り値 ascmc のインデックスに対応

# 日本語・記号辞書 (必要に応じて拡張)
SIGN_JP = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"
]
PLANET_GLYPHS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
    'Asc': 'Asc', 'MC': 'MC',
    'True_Node': '☊', 'Mean_Node': '☊'  # ドラゴンヘッド
}
ASPECT_GLYPHS = {
    'Conjunction': '☌', 'Sextile': '∗', 'Square': '□', 'Trine': '△', 'Opposition': '☍'
}
ASPECT_ANGLES = {
    'Conjunction': 0, 'Sextile': 60, 'Square': 90, 'Trine': 120, 'Opposition': 180
}
# アスペクトオーブ (仮設定 - 天体やアスペクトにより変更可)
DEFAULT_ORB = {
    'Conjunction': 8, 'Sextile': 6, 'Square': 7, 'Trine': 8, 'Opposition': 8
}

# 天体名の日本語対応辞書
PLANET_NAMES_JP = {
    'Sun': '太陽',
    'Moon': '月',
    'Mercury': '水星',
    'Venus': '金星',
    'Mars': '火星',
    'Jupiter': '木星',
    'Saturn': '土星',
    'Uranus': '天王星',
    'Neptune': '海王星',
    'Pluto': '冥王星',
    'Asc': 'ASC',
    'MC': 'MC',
    'True_Node': 'ドラゴンヘッド',
    'Mean_Node': 'ミーンノード',
}

# 予測などで使用する主要な天体リスト（月のノード追加）
PLANETS_FOR_FORECAST = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'True_Node']

def format_degree(degree_within_sign):
    """サイン内度数を度分形式に変換"""
    degree = int(degree_within_sign)
    minute = int(abs(degree_within_sign - degree) * 60) # 念のため絶対値をとる
    return f"{degree}°{minute:02d}'" # 分記号 ' を追加

def get_sign(longitude):
    """黄経からサイン(日本語名)とサイン内度数を取得 (utils.signs を使う)"""
    sign_index = int(longitude // 30)
    sign_degree = longitude % 30
    # utils からインポートした signs (英語名) を基に日本語名を取得
    english_sign_name = signs[sign_index % 12] # 12で割った余りを取る
    sign_jp = get_sign_jp(english_sign_name) # utils の関数を使用
    return sign_jp, sign_degree

def deg_diff(lon1, lon2):
    """2つの角度の差を0-180度の範囲で計算"""
    diff = abs(lon1 - lon2)
    return min(diff, 360 - diff)

def get_house_number(longitude, house_cusps):
    """天体の黄経とハウスカスプ情報からハウス番号を決定"""
    # 12個のハウスカスプが昇順であることを前提とする
    # 例: [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 0] のような場合あり

    # 黄経を0-360度の範囲に正規化 (念のため)
    lon_norm = longitude % 360
    # ハウスカスプも正規化 (swe.houses_ex は通常 0-360 で返すはず)
    cusps_norm = [(c % 360) for c in house_cusps]

    # 1ハウスのカスプ (Ascendant) のインデックスを見つける (通常は0だが念のため)
    # asc_cusp = cusps_norm[0]

    # 11ハウスのカスプから12ハウスのカスプ(Asc)までループ
    for i in range(11):
        cusp_start = cusps_norm[i]
        cusp_end = cusps_norm[i+1]
        # カスプが0度をまたぐ場合の処理
        if cusp_start > cusp_end: # 例: 11室が330度、12室(1室始点)が10度
            if lon_norm >= cusp_start or lon_norm < cusp_end:
                return i + 1 # ハウス番号は1から始まる
        # 通常の処理
        elif lon_norm >= cusp_start and lon_norm < cusp_end:
            return i + 1

    # 12ハウスの判定 (11室カスプ >= lon < 0室カスプ)
    # 上記ループで cusp_start = cusps_norm[11], cusp_end = cusps_norm[0] となるはず
    # ループで判定されなかった場合は12ハウスとみなす
    cusp12_start = cusps_norm[11]
    cusp1_start = cusps_norm[0] # 1室の始点 = 12室の終点

    if cusp12_start > cusp1_start: # 0度をまたぐ場合
        if lon_norm >= cusp12_start or lon_norm < cusp1_start:
             return 12
    elif lon_norm >= cusp12_start and lon_norm < cusp1_start: # 通常 (この条件はcusp12_start > cusp1_startでカバーされるはず)
        return 12

    # どのハウスにも属さない場合 (エラーなど)
    return None # またはエラー処理

def calculate_natal_chart(birth_date, birth_time, birth_place, latitude, longitude, timezone_offset_input, house_system=b'P'):
    """
    ネイタルチャート計算 (タイムゾーン処理を修正)
    timezone_offset_input はフォームからの直接入力値であり、フォールバックまたは検証用として使用する。
    基本的には latitude, longitude からタイムゾーンを特定する。
    """
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    tz = None # tz を初期化
    logging.debug(f"TimezoneFinder result for ({latitude}, {longitude}): {timezone_str}") # ログ追加

    if timezone_str:
        try:
            tz = pytz.timezone(timezone_str)
            logging.debug(f"pytz timezone object created: {tz}") # ログ追加
        except pytz.exceptions.UnknownTimeZoneError:
            logging.warning(f"Unknown timezone: {timezone_str}. Falling back to offset: {timezone_offset_input}") # ログレベル変更
            tz = timezone(timedelta(hours=timezone_offset_input))
    else:
        logging.warning(f"Could not find timezone for {latitude},{longitude}. Falling back to offset: {timezone_offset_input}") # ログレベル変更
        tz = timezone(timedelta(hours=timezone_offset_input))

    dt_naive = datetime.combine(birth_date, birth_time)
    logging.debug(f"Naive datetime: {dt_naive}") # ログ追加

    if hasattr(tz, 'localize'):
        dt_aware = tz.localize(dt_naive)
        used_timezone_offset = dt_aware.utcoffset().total_seconds() / 3600
        logging.debug(f"Aware datetime (pytz localized): {dt_aware}, Used offset: {used_timezone_offset}") # ログ追加
    else: # datetime.timezone の場合
        dt_aware = dt_naive.replace(tzinfo=tz)
        used_timezone_offset = timezone_offset_input # 固定オフセットの場合
        logging.debug(f"Aware datetime (fixed offset): {dt_aware}, Used offset: {used_timezone_offset}") # ログ追加

    dt_utc = dt_aware.astimezone(timezone.utc)
    jd_ut = swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day,
                          dt_utc.hour, dt_utc.minute, dt_utc.second, 1)[1]
    logging.debug(f"Calculated UTC datetime: {dt_utc}") # ログ追加
    logging.debug(f"Calculated Julian Day (UT): {jd_ut}") # ログ追加

    positions = {}
    swe.set_ephe_path('ephe')

    # 天体位置の計算
    for name, planet_id in PLANETS.items():
        pos, retflag = swe.calc_ut(jd_ut, planet_id, swe.FLG_SPEED)
        # pos[0] は 黄経全体
        sign_jp_calc, sign_degree_within_sign = get_sign(pos[0])
        positions[name] = {
            'longitude': pos[0],
            'speed': pos[3],
            'sign': signs[int(pos[0] // 30)],
            'sign_jp': sign_jp_calc,
            'degree': sign_degree_within_sign, # サイン内度数 (0-30)
            'degree_formatted': format_degree(sign_degree_within_sign), # ★サイン内度数を渡すように修正
            'glyph': get_planet_glyph(name),
            'name_jp': PLANET_NAMES_JP.get(name, name)
        }

    # ハウスと感受点(ASC, MC)の計算
    # swe.houses_ex は (house_cusps[1..12], ascmc[0..9]) を返す
    # flags=swe.FLG_SIDEREAL は恒星時を使う場合に必要かも？ 通常のトロピカルでは不要。
    # デフォルトではトロピカルのはずなので、一旦 flags なしで試す
    try:
        cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_system)
    except Exception as e:
        print(f"Error calculating houses: {e}")
        # エラー発生時はハウス関連をNoneにするなどの処理
        cusps = [0.0] * 12 # ダミーデータ
        ascmc = [0.0] * 10 # ダミーデータ
        # または、ここでNoneを返して上位で処理するなど

    # ASC, MC を positions に追加
    for point_name, point_index in POINTS.items():
        # ascmc のインデックス: 0=ASC, 1=MC, 2=ARMC, 3=Vertex, ...
        lon = ascmc[point_index] # 黄経全体
        sign_jp_calc, sign_degree_within_sign = get_sign(lon) # サイン名とサイン内度数を取得
        positions[point_name] = {
            'longitude': lon,
            'speed': 0,
            'sign': signs[int(lon // 30)],
            'sign_jp': sign_jp_calc,
            'degree': sign_degree_within_sign, # サイン内度数 (0-30)
            'degree_formatted': format_degree(sign_degree_within_sign), # ★サイン内度数を渡すように修正
            'glyph': get_planet_glyph(point_name),
            'name_jp': PLANET_NAMES_JP.get(point_name, point_name)
        }

    # 各天体のハウス位置を計算
    house_cusps_list = list(cusps) # タプルをリストに変換
    for name in PLANETS.keys():
        planet_lon = positions[name]['longitude']
        house_number = get_house_number(planet_lon, house_cusps_list)
        positions[name]['house'] = house_number if house_number is not None else 'Error'

    # ASC/MCのハウスを設定 (ASCは1室、MCは10室のカスプだが、天体としてのハウス位置とは意味が異なる場合がある)
    # ASC は定義上常に1ハウスにある (1ハウスの開始点なので)
    # MC は定義上常に10ハウスにある (10ハウスの開始点なので)
    positions['Asc']['house'] = 1
    positions['MC']['house'] = 10

    # 計算に使用した情報を追加
    chart_info = {
        'latitude': latitude,
        'longitude': longitude,
        'timezone': str(tz) if timezone_str else f"UTC{used_timezone_offset:+.1f}", # タイムゾーン名の表示を修正
        'house_system': house_system.decode('utf-8') if isinstance(house_system, bytes) else house_system,
        'used_timezone_offset': used_timezone_offset, # 実際に使われたオフセットも返す
        'jd_ut': jd_ut # ユリウス日も追加
    }
    
    # ハウスシステムの日本語名を追加
    house_system_jp = {
        'P': 'プラシダス', 
        'K': 'コッホ', 
        'O': 'ポルフィリウス',
        'R': 'レジオモンタヌス', 
        'C': 'カンパヌス', 
        'E': '等分', 
        'W': 'ホールサイン',
        'B': 'アルカビチウス'
    }
    
    # バイト型のハウスシステムコードを文字列に変換
    house_system_code = house_system.decode('utf-8') if isinstance(house_system, bytes) else house_system
    
    # 日本語のハウスシステム名を設定
    chart_info['house_system_jp'] = house_system_jp.get(house_system_code, f'不明なシステム（{house_system_code}）')

    swe.close()
    return positions, chart_info, cusps # cusps も返す

def calculate_transit(transit_datetime, birth_date, birth_time, birth_place, latitude, longitude, timezone_offset_input):
    """トランジット計算 (タイムゾーン処理を修正)"""
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    tz = None # tz を初期化

    if timezone_str:
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            print(f"Unknown timezone for transit: {timezone_str}. Falling back to offset.")
            tz = timezone(timedelta(hours=timezone_offset_input))
    else:
        print(f"Could not find timezone for transit at {latitude},{longitude}. Falling back to offset.")
        tz = timezone(timedelta(hours=timezone_offset_input))

    if transit_datetime.tzinfo is None or transit_datetime.tzinfo.utcoffset(transit_datetime) is None:
        if hasattr(tz, 'localize'):
            dt_aware = tz.localize(transit_datetime)
        else:
            dt_aware = transit_datetime.replace(tzinfo=tz)
    else:
        dt_aware = transit_datetime.astimezone(tz)

    dt_utc = dt_aware.astimezone(timezone.utc)
    jd_ut = swe.utc_to_jd(dt_utc.year, dt_utc.month, dt_utc.day,
                          dt_utc.hour, dt_utc.minute, dt_utc.second, 1)[1]

    positions = {}
    swe.set_ephe_path('ephe')

    for name, planet_id in PLANETS.items():
        pos, retflag = swe.calc_ut(jd_ut, planet_id, swe.FLG_SPEED)
        sign_jp_calc, sign_degree_raw = get_sign(pos[0])
        positions[name] = {
            'longitude': pos[0],
            'speed': pos[3],
            'sign': signs[int(pos[0] // 30)],
            'sign_jp': sign_jp_calc,
            'degree': pos[0] % 30,
            'degree_formatted': format_degree(pos[0]),
            'glyph': get_planet_glyph(name),
            'name_jp': PLANET_NAMES_JP.get(name, name)
        }

    swe.close()
    return positions

def calculate_aspects(positions1, positions2=None, orb_degrees=None):
    """
    天体間のアスペクトを計算します。
    positions2が指定されている場合は、positions1(トランジット等)とpositions2(ネイタル等)間のアスペクトを計算します。
    positions2がNoneの場合は、positions1内の天体間のアスペクト(ネイタル等)を計算します。

    Args:
        positions1 (dict): 比較元天体位置辞書 {planet_name: {'longitude': float, ...}}
        positions2 (dict, optional): 比較先天体位置辞書。 Defaults to None.
        orb_degrees (dict, optional): アスペクトタイプごとの許容オーブ。 Defaults to None.

    Returns:
        list: アスペクト情報のリスト [{planet1, planet2, aspect_type, orb, aspect_glyph, planet1_glyph, planet2_glyph, planet1_jp, planet2_jp}, ...]
    """
    if orb_degrees is None:
        # オーブを厳しくして数を減らす（値を小さくする）
        orb_degrees = {
            'Conjunction': 8, 'Opposition': 8, 'Trine': 6, 'Square': 6,
            'Sextile': 4, 'Inconjunct': 1, 'Semisextile': 1, 'Quintile': 1, 'BiQuintile': 1
        }

    aspects = []
    planets1 = list(positions1.keys())

    if positions2 is None: # ネイタルチャート内のアスペクト計算
        # 同じ天体ペアを計算しないように組み合わせを生成
        for i in range(len(planets1)):
            for j in range(i + 1, len(planets1)):
                p1_name = planets1[i]
                p2_name = planets1[j]
                
                # 主要天体のみを対象とする場合
                main_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Asc', 'MC']
                if p1_name not in main_planets or p2_name not in main_planets:
                    continue
                
                p1_lon = positions1[p1_name]['longitude']
                p2_lon = positions1[p2_name]['longitude']

                # 主要なアスペクトをチェック
                for aspect_name, aspect_angle in aspect_types.items():
                    orb = orb_degrees.get(aspect_name, 0) # 定義されてないアスペクトはオーブ0
                    diff = abs(p1_lon - p2_lon)
                    angle_diff = min(diff, 360 - diff) # 0-180度の角度差

                    if abs(angle_diff - aspect_angle) <= orb:
                        # 主要アスペクトのみを含める（マイナーアスペクトを除外）
                        is_major = aspect_name in ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']
                        aspects.append({
                            'planet1': p1_name,
                            'planet2': p2_name,
                            'aspect_type': aspect_name,
                            'orb': round(abs(angle_diff - aspect_angle), 2),
                            'aspect_glyph': get_aspect_glyph(aspect_name),
                            'planet1_glyph': get_planet_glyph(p1_name),
                            'planet2_glyph': get_planet_glyph(p2_name),
                            'planet1_jp': PLANET_NAMES_JP.get(p1_name, p1_name),
                            'planet2_jp': PLANET_NAMES_JP.get(p2_name, p2_name),
                            'is_major': is_major
                        })
                        break # 最初に見つかった主要アスペクトでループを抜ける場合（複数許容しない場合）
    else: # トランジット-ネイタル間のアスペクト計算
        planets2 = list(positions2.keys())
        for p1_name in planets1:
            # トランジット側がASC/MCの場合はスキップ（通常考慮しない）
            if p1_name in ['Asc', 'MC']: continue
            for p2_name in planets2:
                # ネイタル側がASC/MCの場合はハウスとして考慮するためスキップしないことが多いが、
                # ここでは単純な天体間アスペクトのみを計算
                # if p2_name in ['Asc', 'MC']: continue # 必要ならコメント解除

                # 主要天体のみを対象とする場合
                main_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Asc', 'MC']
                if p1_name not in main_planets or p2_name not in main_planets:
                    continue

                p1_lon = positions1[p1_name]['longitude']
                p2_lon = positions2[p2_name]['longitude']

                for aspect_name, aspect_angle in aspect_types.items():
                    orb = orb_degrees.get(aspect_name, 0)
                    diff = abs(p1_lon - p2_lon)
                    angle_diff = min(diff, 360 - diff)

                    if abs(angle_diff - aspect_angle) <= orb:
                        # 主要アスペクトのみを含める
                        is_major = aspect_name in ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']
                        aspects.append({
                            'planet1': p1_name, # Transit Planet
                            'planet2': p2_name, # Natal Planet
                            'aspect_type': aspect_name,
                            'orb': round(abs(angle_diff - aspect_angle), 2),
                            'aspect_glyph': get_aspect_glyph(aspect_name),
                            'planet1_glyph': get_planet_glyph(p1_name),
                            'planet2_glyph': get_planet_glyph(p2_name),
                            'planet1_jp': PLANET_NAMES_JP.get(p1_name, p1_name), # Transit 日本語名
                            'planet2_jp': PLANET_NAMES_JP.get(p2_name, p2_name),  # Natal 日本語名
                            'is_major': is_major
                        })
                        break

    # アスペクトをオーブの小ささ順、または特定の順序でソート（任意）
    aspects.sort(key=lambda x: x['orb'])

    return aspects

# アスペクトグリッド生成関数を修正
def generate_aspect_grid(aspects, planets_order=None):
    if planets_order is None:
        # 表示する天体を限定する
        planets_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Asc', 'MC']
    
    # 指定した天体のみを使用
    planets_to_use = [p for p in planets_order if p in (list(PLANETS.keys()) + list(POINTS.keys()))]

    grid = {p1: {p2: "" for p2 in planets_to_use} for p1 in planets_to_use}

    for aspect in aspects:
        p1, p2 = aspect['planet1'], aspect['planet2']
        
        # グリッドに含まれる天体のみ処理
        if p1 not in planets_to_use or p2 not in planets_to_use:
            continue
            
        aspect_glyph = aspect['aspect_glyph'] # aspect データからグリフを取得
        if p1 in grid and p2 in grid[p1]:
            grid[p1][p2] = aspect_glyph
        if p2 in grid and p1 in grid[p2]: # 対称性を考慮
            grid[p2][p1] = aspect_glyph

    # 対角線にXを入れるなど、必要なら調整
    for p in planets_to_use:
        if p in grid and p in grid[p]:
            grid[p][p] = 'X'

    return {'planets': planets_to_use, 'grid': grid}

def get_planet_details(longitude, planet_name):
    """黄経と惑星名から、サイン、度数、記号などの詳細情報を取得するヘルパー関数"""
    sign_jp, degree_within_sign = get_sign(longitude)
    return {
        'name': planet_name,
        'name_jp': PLANET_NAMES_JP.get(planet_name, planet_name),
        'longitude': longitude,
        'sign': signs[int(longitude // 30) % 12], # 英語サイン名
        'sign_jp': sign_jp,
        'degree': degree_within_sign,
        'degree_formatted': format_degree(degree_within_sign),
        'glyph': get_planet_glyph(planet_name)
    }

def get_current_age(birth_date):
    """生年月日から現在の年齢を計算"""
    today = datetime.now().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def find_solar_longitude_event_jd_ut(year: int, target_longitude: float) -> float:
    """太陽が指定された黄経に到達するユリウス日(UT)を見つける汎用関数"""
    swe.set_ephe_path('ephe')
    
    # ターゲット黄経に基づいて探索開始月を大まかに設定
    # target_longitude: 0 (春分), 90 (夏至), 180 (秋分), 270 (冬至)
    if 0 <= target_longitude < 90: # 春分前後
        search_month = 3
        search_day = 19
    elif 90 <= target_longitude < 180: # 夏至前後
        search_month = 6
        search_day = 19
    elif 180 <= target_longitude < 270: # 秋分前後
        search_month = 9
        search_day = 20 # 少し遅めから
    elif 270 <= target_longitude < 360: # 冬至前後
        search_month = 12
        search_day = 19
    else:
        raise ValueError("Target longitude must be between 0 and 359.")

    jd_start_search = swe.utc_to_jd(year, search_month, search_day, 0, 0, 0, 1)[1]
    jd_event_ut = jd_start_search # 初期値

    # 1時間ごとにチェック (約3日分を探索)
    for h in range(24 * 4): # 余裕をもって4日分
        current_jd_ut = jd_start_search + h / 24.0
        sun_pos, _ = swe.calc_ut(current_jd_ut, swe.SUN, swe.FLG_SWIEPH)
        sun_lon = sun_pos[0]

        if h > 0:
            prev_sun_pos, _ = swe.calc_ut(jd_start_search + (h - 1) / 24.0, swe.SUN, swe.FLG_SWIEPH)
            prev_sun_lon = prev_sun_pos[0]

            # 黄経がターゲット度数をまたいだかどうかの判定を一般化
            # 例: target=90 の場合、88 -> 91 のような変化を探す
            # prev_sun_lon が target_longitude より小さく、sun_lon が target_longitude 以上になる瞬間
            # またはその逆（逆行は考慮しない前提だが、黄経0度をまたぐ場合は特別扱いが必要）

            # 0度(360度)をまたぐ場合の処理 (春分点、またはtarget_longitudeが0に近い場合)
            if target_longitude < 10 and prev_sun_lon > 350 and sun_lon < 10: # 350度台から10度未満へ
                 is_crossed = True
            # 0度をまたがない通常のケース
            elif prev_sun_lon < target_longitude and sun_lon >= target_longitude:
                is_crossed = True
            # ターゲット度数直前で計算が終了しないように、少し幅を持たせる (例: 89.9 -> 90.1)
            elif abs(sun_lon - target_longitude) < 1.0 and abs(prev_sun_lon - target_longitude) > abs(sun_lon - target_longitude):
                is_crossed = True # よりターゲットに近い方に進んだ
            else:
                is_crossed = False

            if is_crossed:
                # より正確な時刻を分単位で探索
                jd_hour_start = jd_start_search + (h - 1) / 24.0 # クロスした1時間の開始時刻
                for m in range(60):
                    current_jd_ut_minute = jd_hour_start + m / (24.0 * 60.0)
                    sun_pos_minute, _ = swe.calc_ut(current_jd_ut_minute, swe.SUN, swe.FLG_SWIEPH)
                    sun_lon_minute = sun_pos_minute[0]
                    
                    # 分単位でのクロス判定 (0度またぎも考慮)
                    prev_sun_lon_minute, _ = swe.calc_ut(jd_hour_start + (m-1 if m > 0 else 0) / (24.0 * 60.0), swe.SUN, swe.FLG_SWIEPH)
                    prev_sun_lon_minute = prev_sun_lon_minute[0]

                    is_crossed_minute = False
                    if target_longitude < 10 and prev_sun_lon_minute > 350 and sun_lon_minute < 10:
                        is_crossed_minute = True
                    elif prev_sun_lon_minute < target_longitude and sun_lon_minute >= target_longitude:
                        is_crossed_minute = True
                    
                    if is_crossed_minute:
                        # ターゲット度数に最も近い時刻を選ぶ (より簡潔な方法: swe.revtrans etc. の利用検討)
                        # ここでは、クロスした直後の時刻を採用する
                        jd_event_ut = current_jd_ut_minute
                        logging.debug(f"Solar event at lon {target_longitude} found near UT JD: {jd_event_ut}")
                        swe.close()
                        return jd_event_ut
                # 分単位で見つからなければ、時間単位のクロス直後の時刻を採用
                jd_event_ut = current_jd_ut
                logging.debug(f"Solar event at lon {target_longitude} (hourly precision) found near UT JD: {jd_event_ut}")
                swe.close()
                return jd_event_ut
    
    logging.warning(f"Solar event at lon {target_longitude} NOT precisely found, using rough estimate (end of search period).")
    swe.close()
    return jd_event_ut # 見つからなければ探索期間の最後の方の値を返す (要改善)

def calculate_celestial_sabian_at_event(jd_ut_event: float, event_name: str):
    """指定されたユリウス日(UT)における各天体のサビアンシンボルを計算する関数"""
    swe.set_ephe_path('ephe')
    event_planet_data = []
    logging.debug(f"Calculating Sabian symbols for {event_name} at JD_UT: {jd_ut_event}")

    # ポジションの計算結果をディクショナリ形式でも保持
    event_positions = {}

    for planet_name in PLANETS_FOR_FORECAST:
        planet_id = PLANETS.get(planet_name)
        if planet_id is None:
            logging.warning(f"{event_name}: Planet ID not found for {planet_name}, skipping.")
            continue

        pos, _ = swe.calc_ut(jd_ut_event, planet_id, swe.FLG_SWIEPH)
        longitude = pos[0]
        
        planet_details = get_planet_details(longitude, planet_name)
        sabian_symbol = get_sabian_symbol(longitude)
        logging.debug(f"{event_name} Data for {planet_name}: lon={longitude}, sabian='{sabian_symbol}'")

        # リスト形式のデータ
        event_planet_data.append({
            'name': planet_name,
            'name_jp': PLANET_NAMES_JP.get(planet_name, planet_name),
            'longitude': longitude,
            'sign': planet_details['sign'],
            'sign_jp': planet_details['sign_jp'],
            'degree_in_sign_decimal': planet_details['degree'],
            'degree_formatted': planet_details['degree_formatted'],
            'sabian_symbol': sabian_symbol,
            'glyph': get_planet_glyph(planet_name)
        })
        
        # ディクショナリ形式のデータ（ホロスコープチャート生成用）
        event_positions[planet_name] = {
            'longitude': longitude,
            'sign': planet_details['sign'],
            'sign_jp': planet_details['sign_jp'],
            'degree': planet_details['degree'],
            'degree_formatted': planet_details['degree_formatted'],
            'glyph': get_planet_glyph(planet_name),
            'name_jp': PLANET_NAMES_JP.get(planet_name, planet_name)
        }
    
    # ASC/MCの計算（東京の緯度経度を使用）
    latitude_tokyo = 35.6895
    longitude_tokyo = 139.6917
    house_system = b'P'  # Placidus
    
    try:
        cusps, ascmc = swe.houses_ex(jd_ut_event, latitude_tokyo, longitude_tokyo, house_system)
        
        # ASC, MC を positions に追加
        for point_name, point_index in POINTS.items():
            # ascmc のインデックス: 0=ASC, 1=MC
            lon = ascmc[point_index]
            planet_details = get_planet_details(lon, point_name)
            
            event_positions[point_name] = {
                'longitude': lon,
                'sign': planet_details['sign'],
                'sign_jp': planet_details['sign_jp'],
                'degree': planet_details['degree'],
                'degree_formatted': planet_details['degree_formatted'],
                'glyph': get_planet_glyph(point_name),
                'name_jp': PLANET_NAMES_JP.get(point_name, point_name)
            }
    except Exception as e:
        logging.error(f"Error calculating houses for seasonal chart: {e}")
    
    # アスペクトの計算
    aspects = calculate_aspects(event_positions)
    
    # チャート情報の生成
    chart_info = {
        'house_system': 'Placidus',
        'house_system_jp': 'プラシダス',
        'timezone': 'UTC+9:00',
        'event_name': event_name
    }
    
    swe.close()
    return {
        'sabian_data': event_planet_data,  # サビアンシンボル情報（リスト形式）
        'positions': event_positions,      # 天体位置情報（ディクショナリ形式）
        'aspects': aspects,                # アスペクト情報
        'chart_info': chart_info,          # チャート設定情報
        'cusps': cusps                     # ハウスカスプ情報
    }

def calculate_vernal_equinox_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の春分点の各天体のサビアンシンボルとホロスコープチャートデータを計算 (東京基準)"""
    # 春分点 (太陽黄経0度) のユリウス日(UT)を見つける
    jd_vernal_equinox_ut = find_solar_longitude_event_jd_ut(year, 0.0)
    
    # その瞬間の各天体のサビアン情報とチャートデータを計算
    vernal_equinox_data = calculate_celestial_sabian_at_event(jd_vernal_equinox_ut, f"{year}年 春分点")
    
    return vernal_equinox_data

def calculate_summer_solstice_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の夏至点の各天体のサビアンシンボルとホロスコープチャートデータを計算 (東京基準)"""
    jd_summer_solstice_ut = find_solar_longitude_event_jd_ut(year, 90.0)
    summer_solstice_data = calculate_celestial_sabian_at_event(jd_summer_solstice_ut, f"{year}年 夏至点")
    return summer_solstice_data

def calculate_autumnal_equinox_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の秋分点の各天体のサビアンシンボルとホロスコープチャートデータを計算 (東京基準)"""
    jd_autumnal_equinox_ut = find_solar_longitude_event_jd_ut(year, 180.0)
    autumnal_equinox_data = calculate_celestial_sabian_at_event(jd_autumnal_equinox_ut, f"{year}年 秋分点")
    return autumnal_equinox_data

def calculate_winter_solstice_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の冬至点の各天体のサビアンシンボルとホロスコープチャートデータを計算 (東京基準)"""
    jd_winter_solstice_ut = find_solar_longitude_event_jd_ut(year, 270.0)
    winter_solstice_data = calculate_celestial_sabian_at_event(jd_winter_solstice_ut, f"{year}年 冬至点")
    return winter_solstice_data

def calculate_solar_arc_sabian_forecast(birth_date, birth_time, birth_place, latitude, longitude, timezone_offset_input, years_to_forecast=3):
    """ソーラーアーク法によるサビアン予測 (年齢計算を修正)"""
    swe.set_ephe_path('ephe')
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    tz = None
    if timezone_str:
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            tz = timezone(timedelta(hours=timezone_offset_input))
    else:
        tz = timezone(timedelta(hours=timezone_offset_input))

    dt_naive = datetime.combine(birth_date, birth_time)
    if hasattr(tz, 'localize'):
        dt_aware_birth = tz.localize(dt_naive)
    else:
        dt_aware_birth = dt_naive.replace(tzinfo=tz)
    
    jd_ut_birth = swe.utc_to_jd(
        dt_aware_birth.year, dt_aware_birth.month, dt_aware_birth.day,
        dt_aware_birth.hour, dt_aware_birth.minute, dt_aware_birth.second, 1
    )[1]

    # 進行計算のための太陽の位置 (ネイタル)
    sun_pos_natal, _ = swe.calc_ut(jd_ut_birth, swe.SUN, swe.FLG_SPEED)
    natal_sun_longitude = sun_pos_natal[0]

    forecast_data = []
    current_actual_age = get_current_age(birth_date) # 現在の実年齢を取得

    for i in range(years_to_forecast):
        # 年齢の計算: 1年目 = 現在の年齢, 2年目 = 現在の年齢+1, ...
        age_for_forecast_year = current_actual_age + i 
        
        # ソーラーアーク進行度数 (1年1度法)
        solar_arc_progression = age_for_forecast_year # 単純に年齢を度数として加算

        yearly_planets_data = []
        for planet_name in PLANETS_FOR_FORECAST: # PLANETS_FOR_FORECAST を使用
            planet_id = PLANETS[planet_name]
            
            # ネイタル天体位置を取得 (ここでは速度は不要なので swe.FLG_SWIEPH のみ)
            natal_planet_pos, _ = swe.calc_ut(jd_ut_birth, planet_id, swe.FLG_SWIEPH) # swe.FLG_SPEED は不要
            natal_planet_longitude = natal_planet_pos[0]

            # 進行後の黄経
            progressed_longitude = (natal_planet_longitude + solar_arc_progression) % 360
            
            planet_details = get_planet_details(progressed_longitude, planet_name)
            sabian_symbol = get_sabian_symbol(progressed_longitude)

            yearly_planets_data.append({
                'name': planet_name,
                'name_jp': PLANET_NAMES_JP.get(planet_name, planet_name),
                'longitude': progressed_longitude,
                'sign': planet_details['sign'],
                'sign_jp': planet_details['sign_jp'],
                'degree_in_sign_decimal': planet_details['degree'], # 10進数表記のサイン内度数
                'degree_formatted': planet_details['degree_formatted'],
                'sabian_symbol': sabian_symbol,
                'glyph': get_planet_glyph(planet_name)
            })
        
        forecast_data.append({
            'year_offset': i + 1, # 1年目, 2年目, ...
            'age': age_for_forecast_year, # 予測時の年齢
            'planets': yearly_planets_data
        })

    swe.close()
    return forecast_data

def calculate_secondary_progression(birth_date, birth_time, birth_place, latitude, longitude, 
                                    timezone_offset_input, years_to_forecast=3):
    """二次進行法による天体位置計算（1日=1年の法則）
    
    Args:
        birth_date (date): 誕生日
        birth_time (time): 誕生時間
        birth_place (str): 出生地
        latitude (float): 緯度
        longitude (float): 経度
        timezone_offset_input (float): タイムゾーンオフセット
        years_to_forecast (int, optional): 計算する年数. デフォルトは3年.
    
    Returns:
        list: 各年の進行天体位置情報
    """
    swe.set_ephe_path('ephe')
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    tz = None
    if timezone_str:
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            tz = timezone(timedelta(hours=timezone_offset_input))
    else:
        tz = timezone(timedelta(hours=timezone_offset_input))

    dt_naive = datetime.combine(birth_date, birth_time)
    if hasattr(tz, 'localize'):
        dt_aware_birth = tz.localize(dt_naive)
    else:
        dt_aware_birth = dt_naive.replace(tzinfo=tz)
    
    jd_ut_birth = swe.utc_to_jd(
        dt_aware_birth.year, dt_aware_birth.month, dt_aware_birth.day,
        dt_aware_birth.hour, dt_aware_birth.minute, dt_aware_birth.second, 1
    )[1]

    forecast_data = []
    current_actual_age = get_current_age(birth_date)

    for i in range(years_to_forecast):
        # 現在の年齢 + i年後
        age_for_forecast_year = current_actual_age + i
        
        # 二次進行法: 誕生日からage_for_forecast_year日後の天体位置を計算
        # 1日=1年の法則
        progressed_jd = jd_ut_birth + age_for_forecast_year
        
        yearly_planets_data = []
        for planet_name in PLANETS_FOR_FORECAST:
            planet_id = PLANETS[planet_name]
            
            # 進行後の天体位置を計算
            pos, retflag = swe.calc_ut(progressed_jd, planet_id, swe.FLG_SPEED)
            
            longitude = pos[0]
            planet_details = get_planet_details(longitude, planet_name)
            sabian_symbol = get_sabian_symbol(longitude)
            
            yearly_planets_data.append({
                'name': planet_name,
                'name_jp': PLANET_NAMES_JP.get(planet_name, planet_name),
                'longitude': longitude,
                'sign': planet_details['sign'],
                'sign_jp': planet_details['sign_jp'],
                'degree_in_sign_decimal': planet_details['degree'], 
                'degree_formatted': planet_details['degree_formatted'],
                'sabian_symbol': sabian_symbol,
                'glyph': get_planet_glyph(planet_name),
                'retrograde': pos[3] < 0  # 逆行情報も追加
            })
        
        # 進行時の日付を計算 (天文学的な日付、実際の誕生日からの進行ではない)
        progressed_date = jd_to_datetime(progressed_jd)
        
        forecast_data.append({
            'year_offset': i + 1, # 1年目, 2年目, ...
            'age': age_for_forecast_year, # 予測時の年齢
            'progressed_date': progressed_date.strftime('%Y-%m-%d'), # 進行日付
            'planets': yearly_planets_data
        })

    swe.close()
    return forecast_data

def jd_to_datetime(jd):
    """ユリウス日から日時オブジェクトへの変換"""
    dt_tuple = swe.jdut1_to_utc(jd)
    return datetime(dt_tuple[0], dt_tuple[1], dt_tuple[2], 
                  dt_tuple[3], dt_tuple[4], int(dt_tuple[5])) 

# シナストリー（相性）計算機能
def calculate_synastry_aspects(positions1, positions2, orb_degrees=None):
    """
    2人のホロスコープ間のアスペクトを計算します。

    Args:
        positions1 (dict): 人物1の天体位置データ {planet_name: {'longitude': float, ...}}
        positions2 (dict): 人物2の天体位置データ {planet_name: {'longitude': float, ...}}
        orb_degrees (dict, optional): アスペクトタイプごとの許容オーブ。 Defaults to None.

    Returns:
        list: シナストリーアスペクト情報のリスト。各要素はdict形式で
             {person1_planet, person2_planet, aspect_type, orb, aspect_glyph, ...}
    """
    if orb_degrees is None:
        # シナストリー用のオーブ（通常より少し狭め）
        orb_degrees = {
            'Conjunction': 8, 'Opposition': 8, 'Trine': 7, 'Square': 7,
            'Sextile': 5, 'Inconjunct': 2, 'Semisextile': 2, 'Quintile': 2, 'BiQuintile': 2
        }

    synastry_aspects = []
    planets1 = sorted(list(positions1.keys()), key=lambda p: PLANETS.get(p, 999) if p in PLANETS else 999)
    planets2 = sorted(list(positions2.keys()), key=lambda p: PLANETS.get(p, 999) if p in PLANETS else 999)

    # 人物1の天体 対 人物2の天体のアスペクト計算
    for p1_name in planets1:
        # ASC/MCも含める場合は以下の条件文を削除
        if p1_name in ['Asc', 'MC']: continue

        for p2_name in planets2:
            # ASC/MCも含める場合は以下の条件文を削除
            if p2_name in ['Asc', 'MC']: continue

            p1_lon = positions1[p1_name]['longitude']
            p2_lon = positions2[p2_name]['longitude']

            # 各アスペクトタイプをチェック
            for aspect_name, aspect_angle in aspect_types.items():
                orb = orb_degrees.get(aspect_name, 0)
                diff = abs(p1_lon - p2_lon)
                angle_diff = min(diff, 360 - diff)

                if abs(angle_diff - aspect_angle) <= orb:
                    synastry_aspects.append({
                        'person1_planet': p1_name,
                        'person2_planet': p2_name,
                        'aspect_type': aspect_name,
                        'orb': round(abs(angle_diff - aspect_angle), 2),
                        'aspect_glyph': get_aspect_glyph(aspect_name),
                        'person1_planet_glyph': get_planet_glyph(p1_name),
                        'person2_planet_glyph': get_planet_glyph(p2_name),
                        'person1_planet_jp': PLANET_NAMES_JP.get(p1_name, p1_name),
                        'person2_planet_jp': PLANET_NAMES_JP.get(p2_name, p2_name)
                    })
                    break  # 一つのアスペクトが見つかったらループを抜ける

    # アスペクトをオーブの小ささ順にソート
    synastry_aspects.sort(key=lambda x: x['orb'])

    return synastry_aspects

def calculate_composite_chart(positions1, positions2):
    """
    2人の出生図から合成図（コンポジットチャート）を計算します。
    各天体の中間点を計算し、合成図の天体位置とします。

    Args:
        positions1 (dict): 人物1の天体位置データ {planet_name: {'longitude': float, ...}}
        positions2 (dict): 人物2の天体位置データ {planet_name: {'longitude': float, ...}}

    Returns:
        dict: 合成図の天体位置データ
    """
    composite_positions = {}
    common_planets = set(positions1.keys()) & set(positions2.keys())

    for planet in common_planets:
        lon1 = positions1[planet]['longitude']
        lon2 = positions2[planet]['longitude']

        # 中間点計算（0-360度をまたぐ場合に対応）
        # 例: 350度と10度の中間点は0度（180度ではない）
        diff = abs(lon1 - lon2)
        if diff > 180:
            # 短い方の円弧で中間点を計算
            min_lon = min(lon1, lon2)
            max_lon = max(lon1, lon2)
            # 0度をまたぐ場合
            midpoint = (min_lon + max_lon + 360) / 2 % 360
        else:
            # 通常の中間点計算
            midpoint = (lon1 + lon2) / 2

        # サインの計算
        sign_jp, degree_within_sign = get_sign(midpoint)
        sign_index = int(midpoint // 30)
        sign = signs[sign_index % 12]

        composite_positions[planet] = {
            'longitude': midpoint,
            'sign': sign,
            'sign_jp': sign_jp,
            'degree': degree_within_sign,
            'degree_formatted': format_degree(degree_within_sign),
            'glyph': get_planet_glyph(planet),
            'name_jp': PLANET_NAMES_JP.get(planet, planet)
        }

    return composite_positions

def calculate_synastry(person1_data, person2_data):
    """
    2人の出生データからシナストリー（相性）情報を計算します。

    Args:
        person1_data (dict): 人物1の出生データ（natal_chart計算結果）
        person2_data (dict): 人物2の出生データ（natal_chart計算結果）

    Returns:
        dict: シナストリー情報（アスペクト、合成図）
    """
    # 2人間のアスペクト計算
    synastry_aspects = calculate_synastry_aspects(
        person1_data['positions'], 
        person2_data['positions']
    )
    
    # 合成図（コンポジット）計算
    composite_positions = calculate_composite_chart(
        person1_data['positions'], 
        person2_data['positions']
    )
    
    # 合成図内のアスペクト計算
    composite_aspects = calculate_aspects(composite_positions)
    
    return {
        'synastry_aspects': synastry_aspects,
        'composite_positions': composite_positions,
        'composite_aspects': composite_aspects
    } 

# 新しい関数：月のノード（ドラゴンヘッド/テイル）の位置を計算
def calculate_lunar_nodes(jd_ut):
    """
    月のノード（ドラゴンヘッド/テイル）の位置を計算する
    
    Args:
        jd_ut (float): ユリウス日（UT）
    
    Returns:
        dict: 月のノード情報を含む辞書
    """
    swe.set_ephe_path('ephe')
    
    nodes = {}
    
    # ドラゴンヘッド (True Node)
    true_node_pos, retflag = swe.calc_ut(jd_ut, swe.TRUE_NODE, swe.FLG_SPEED)
    sign_jp_calc, sign_degree_within_sign = get_sign(true_node_pos[0])
    nodes['True_Node'] = {
        'longitude': true_node_pos[0],
        'speed': true_node_pos[3],
        'sign': signs[int(true_node_pos[0] // 30)],
        'sign_jp': sign_jp_calc,
        'degree': sign_degree_within_sign,
        'degree_formatted': format_degree(sign_degree_within_sign),
        'glyph': get_planet_glyph('True_Node'),
        'name_jp': PLANET_NAMES_JP.get('True_Node', 'True_Node'),
        'retrograde': true_node_pos[3] < 0
    }
    
    # ミーンノード (Mean Node)
    mean_node_pos, retflag = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SPEED)
    sign_jp_calc, sign_degree_within_sign = get_sign(mean_node_pos[0])
    nodes['Mean_Node'] = {
        'longitude': mean_node_pos[0],
        'speed': mean_node_pos[3],
        'sign': signs[int(mean_node_pos[0] // 30)],
        'sign_jp': sign_jp_calc,
        'degree': sign_degree_within_sign,
        'degree_formatted': format_degree(sign_degree_within_sign),
        'glyph': get_planet_glyph('Mean_Node'),
        'name_jp': PLANET_NAMES_JP.get('Mean_Node', 'Mean_Node'),
        'retrograde': mean_node_pos[3] < 0
    }
    
    # ドラゴンテイル（ケツ）の計算 - ドラゴンヘッドから180度反対側
    tail_longitude = (nodes['True_Node']['longitude'] + 180) % 360
    sign_jp_calc, sign_degree_within_sign = get_sign(tail_longitude)
    nodes['Dragon_Tail'] = {
        'longitude': tail_longitude,
        'speed': nodes['True_Node']['speed'], # ヘッドと同じ速度
        'sign': signs[int(tail_longitude // 30)],
        'sign_jp': sign_jp_calc,
        'degree': sign_degree_within_sign,
        'degree_formatted': format_degree(sign_degree_within_sign),
        'glyph': '☋',  # ドラゴンテイル（ケツ）の記号
        'name_jp': 'ドラゴンテイル'
    }
    
    return nodes

# 月のノードの解釈文データ
NODE_INTERPRETATIONS = {
    'True_Node': {
        "牡羊座": "ドラゴンヘッドが牡羊座にあることは、あなたが魂の成長において個人的なアイデンティティ、自己主張、そして新しいスタートを経験する必要があることを示しています。人生での使命は、勇気を持って自分自身を表現し、リーダーシップを発揮することです。前世では他者に依存しすぎていたかもしれず、このライフではより独立的になることが魂の課題となっています。",
        "牡牛座": "ドラゴンヘッドが牡牛座にあることは、あなたが魂の成長において物質的な安定、価値観の確立、そして感覚的な喜びを経験する必要があることを示しています。人生での使命は、忍耐と決意を持って実質的な成果を築き上げることです。前世では物質に執着しすぎなかったかもしれず、このライフでは地に足をつけた安定感を得ることが魂の課題となっています。",
        "双子座": "ドラゴンヘッドが双子座にあることは、あなたが魂の成長においてコミュニケーション、知的好奇心、そして多様性を経験する必要があることを示しています。人生での使命は、情報を収集し、共有し、さまざまな視点から物事を見ることです。前世では深く掘り下げることなく表面的な知識に留まっていたかもしれず、このライフではより詳細に学ぶことが魂の課題となっています。",
        "蟹座": "ドラゴンヘッドが蟹座にあることは、あなたが魂の成長において感情的なつながり、家族、そして内なる安全を経験する必要があることを示しています。人生での使命は、深い感情的な絆を育み、自分の感情を完全に受け入れることです。前世では感情を抑制しすぎていたかもしれず、このライフではより感情的に開かれることが魂の課題となっています。",
        "獅子座": "ドラゴンヘッドが獅子座にあることは、あなたが魂の成長において創造的な自己表現、情熱、そして本物の自己を経験する必要があることを示しています。人生での使命は、自分の創造力を通じて喜びと愛を世界に広めることです。前世では背景に留まりすぎていたかもしれず、このライフではより中心的な役割を果たすことが魂の課題となっています。",
        "乙女座": "ドラゴンヘッドが乙女座にあることは、あなたが魂の成長において実用的なスキル、分析能力、そして健康的な生活習慣を経験する必要があることを示しています。人生での使命は、細部に注意を払い、日常生活で秩序と効率を確立することです。前世では大きな絵を見るのに忙しすぎて詳細を見逃していたかもしれず、このライフではより実用的になることが魂の課題となっています。",
        "天秤座": "ドラゴンヘッドが天秤座にあることは、あなたが魂の成長において関係性、調和、そして公平さを経験する必要があることを示しています。人生での使命は、バランスを見つけ、パートナーシップを通じて成長することです。前世では自分自身に焦点を当てすぎていたかもしれず、このライフではより他者との相互作用に重点を置くことが魂の課題となっています。",
        "蠍座": "ドラゴンヘッドが蠍座にあることは、あなたが魂の成長において変容、共有資源、そして深い親密さを経験する必要があることを示しています。人生での使命は、魂の深みを探求し、強力な癒しの変容を経験することです。前世では表面的な関係に留まりすぎていたかもしれず、このライフではより深いレベルで自分自身と他者を理解することが魂の課題となっています。",
        "射手座": "ドラゴンヘッドが射手座にあることは、あなたが魂の成長において高等教育、旅行、そして形而上学的な真理を経験する必要があることを示しています。人生での使命は、より広い視野を持ち、信念体系を拡大することです。前世では狭い視野に囚われすぎていたかもしれず、このライフではより広い視点を持つことが魂の課題となっています。",
        "山羊座": "ドラゴンヘッドが山羊座にあることは、あなたが魂の成長において構造、権威、そして長期的な成功を経験する必要があることを示しています。人生での使命は、責任を持ち、社会的な貢献を通じて成長することです。前世では責任を避けすぎていたかもしれず、このライフではより規律正しくなることが魂の課題となっています。",
        "水瓶座": "ドラゴンヘッドが水瓶座にあることは、あなたが魂の成長において革新、コミュニティ、そして人道的な理想を経験する必要があることを示しています。人生での使命は、独自の視点を持ち、社会的変革に貢献することです。前世では因襲的な思考に囚われすぎていたかもしれず、このライフではより前衛的になることが魂の課題となっています。",
        "魚座": "ドラゴンヘッドが魚座にあることは、あなたが魂の成長において精神性、直感、そして無条件の愛を経験する必要があることを示しています。人生での使命は、より高い意識状態に接続し、宇宙の流れに身を委ねることです。前世では現実的な懸念に焦点を当てすぎていたかもしれず、このライフではより霊的な次元を探求することが魂の課題となっています。"
    },
    'Dragon_Tail': {
        "牡羊座": "ドラゴンテイルが牡羊座にあることは、あなたが前世で個人的な欲求や衝動に焦点を当てすぎていた可能性を示唆しています。このライフでは、より協力的で思いやりのある姿勢を学ぶ必要があります。自己中心的になりがちな傾向や独断的な行動パターンを克服することが魂の課題です。",
        "牡牛座": "ドラゴンテイルが牡牛座にあることは、あなたが前世で物質的な所有や安定に執着しすぎていた可能性を示唆しています。このライフでは、より精神的な価値観を育み、執着を手放すことを学ぶ必要があります。物質主義や頑固さを克服することが魂の課題です。",
        "双子座": "ドラゴンテイルが双子座にあることは、あなたが前世で表面的な知識や情報に散漫になりすぎていた可能性を示唆しています。このライフでは、より深い真実や哲学的な理解を追求する必要があります。うわべだけの会話や落ち着きのなさを克服することが魂の課題です。",
        "蟹座": "ドラゴンテイルが蟹座にあることは、あなたが前世で感情的な依存や過保護な態度に陥りすぎていた可能性を示唆しています。このライフでは、より自立し、感情に振り回されない強さを育む必要があります。過去への執着や感情的な不安定さを克服することが魂の課題です。",
        "獅子座": "ドラゴンテイルが獅子座にあることは、あなたが前世でプライドや自己中心的な創造性に焦点を当てすぎていた可能性を示唆しています。このライフでは、より謙虚になり、他者のニーズや集団の福祉に貢献することを学ぶ必要があります。自己顕示欲や支配的な傾向を克服することが魂の課題です。",
        "乙女座": "ドラゴンテイルが乙女座にあることは、あなたが前世で批判的になりすぎたり、細部にこだわりすぎていた可能性を示唆しています。このライフでは、より全体的な視点を持ち、完璧主義を手放すことを学ぶ必要があります。過度の分析や不必要な心配を克服することが魂の課題です。",
        "天秤座": "ドラゴンテイルが天秤座にあることは、あなたが前世で他者に依存しすぎたり、決断を避けすぎていた可能性を示唆しています。このライフでは、より自立し、自分自身の判断に従うことを学ぶ必要があります。優柔不断さや表面的な調和への執着を克服することが魂の課題です。",
        "蠍座": "ドラゴンテイルが蠍座にあることは、あなたが前世で力の追求や感情的な操作に陥りすぎていた可能性を示唆しています。このライフでは、より透明性と信頼を育み、執着や復讐心を手放すことを学ぶ必要があります。強い支配欲や秘密主義を克服することが魂の課題です。",
        "射手座": "ドラゴンテイルが射手座にあることは、あなたが前世で過度に理想主義的だったり、自分の信念を押し付けすぎていた可能性を示唆しています。このライフでは、より実践的で開かれた心を持つことを学ぶ必要があります。独断的な姿勢や過剰な楽観主義を克服することが魂の課題です。",
        "山羊座": "ドラゴンテイルが山羊座にあることは、あなたが前世で社会的地位や成功に執着しすぎていた可能性を示唆しています。このライフでは、より内面的な満足感を見出し、柔軟性を育むことを学ぶ必要があります。過度の野心や厳格さを克服することが魂の課題です。",
        "水瓶座": "ドラゴンテイルが水瓶座にあることは、あなたが前世で革新や独立性を追求するあまり、人間的なつながりを犠牲にしていた可能性を示唆しています。このライフでは、より温かみのある関係を育み、個人的な絆を大切にすることを学ぶ必要があります。過度の分離や感情的な切り離しを克服することが魂の課題です。",
        "魚座": "ドラゴンテイルが魚座にあることは、あなたが前世で現実逃避や犠牲者意識に陥りすぎていた可能性を示唆しています。このライフでは、より実践的で自己責任のある姿勢を育むことを学ぶ必要があります。幻想や依存傾向、境界の曖昧さを克服することが魂の課題です。"
    }
}

# 重要なライフイベント予測機能を実装
def predict_life_events(natal_positions, forecast_years=5):
    """
    トランジットとプログレッションを組み合わせた重要ライフイベント予測
    
    Args:
        natal_positions (dict): ネイタルチャートの天体位置データ
        forecast_years (int): 予測する年数（デフォルト5年間）
    
    Returns:
        list: 予測される重要ライフイベントのリスト（日付、イベント内容、強度を含む）
    """
    swe.set_ephe_path('ephe')
    current_date = datetime.now()
    current_year = current_date.year
    
    # 結果を格納するリスト
    life_events = []
    
    # 主要天体のトランジットからの予測
    transit_planets = ['Saturn', 'Jupiter', 'Uranus', 'Neptune', 'Pluto', 'True_Node']
    natal_key_points = ['Sun', 'Moon', 'Asc', 'MC', 'True_Node'] + list(natal_positions.keys())
    
    # 重要なアスペクト角度とその意味
    important_aspects = {
        0: "コンジャンクション（合）- 強力なエネルギーの融合と新しい始まり",
        60: "セクスタイル（六分）- 協調的な機会とスムーズな進展",
        90: "スクエア（四分）- 緊張、挑戦、行動への呼びかけ",
        120: "トライン（三分）- 調和的な流れと自然な才能の発揮",
        180: "オポジション（対向）- 対立、バランス、関係性の再調整"
    }
    
    # イベントの内容と対応するアスペクト
    event_types = {
        ('Jupiter', 'Sun', 0): "成功と拡大のチャンス、認識の高まり",
        ('Jupiter', 'Sun', 120): "成長と好機の時期、楽観的な姿勢が報われる",
        ('Jupiter', 'Moon', 0): "感情的な充実感と家庭の幸福",
        ('Jupiter', 'Asc', 0): "個人的な成長と新しい機会",
        ('Jupiter', 'MC', 0): "キャリアの進展と社会的認知",
        ('Saturn', 'Sun', 90): "責任の増加と挑戦、重要な決断の時期",
        ('Saturn', 'Sun', 180): "重要な人生の岐路、責任と現実との対峙",
        ('Saturn', 'Moon', 90): "感情的な制約と自己規律の必要性",
        ('Saturn', 'Asc', 0): "個人的アイデンティティの再構築",
        ('Saturn', 'MC', 0): "キャリアの転機と長期目標の再評価",
        ('Uranus', 'Sun', 0): "突然の変化と解放、自己認識の変革",
        ('Uranus', 'Moon', 90): "感情的な不安定さと予期せぬ変化",
        ('Uranus', 'Asc', 90): "ライフスタイルの急激な変化と新しい表現方法",
        ('Uranus', 'MC', 90): "キャリアの突然の変化、新しい方向性",
        ('Neptune', 'Sun', 90): "理想と現実の間の混乱、創造性の高まり",
        ('Neptune', 'Moon', 90): "感情的な混乱と精神的な気づき",
        ('Neptune', 'Asc', 0): "アイデンティティの再定義、精神的な覚醒",
        ('Neptune', 'MC', 90): "キャリアの方向性が不明確になる時期",
        ('Pluto', 'Sun', 0): "深い変容とパワーの課題、再生",
        ('Pluto', 'Moon', 90): "深い感情的な変容と内面の力の発見",
        ('Pluto', 'Asc', 90): "強烈な自己変革、古い自己の死と再生",
        ('Pluto', 'MC', 0): "キャリアと社会的地位の根本的な変化",
        ('True_Node', 'Sun', 0): "運命的な出会いと魂の目的の実現",
        ('True_Node', 'Moon', 0): "カルマ的な感情パターンとの対面",
        ('True_Node', 'Asc', 0): "人生の方向性の重要な転換点",
    }
    
    # 異なる年（現在から最大5年後まで）のトランジットをチェック
    for year_offset in range(forecast_years + 1):
        check_year = current_year + year_offset
        
        # 各月をチェック
        for month in range(1, 13):
            if year_offset == 0 and month < current_date.month:
                continue  # 過去の月はスキップ
                
            # 月の半ばの日付を使用
            check_date = datetime(check_year, month, 15)
            jd_ut = swe.julday(check_date.year, check_date.month, check_date.day)
            
            # トランジット天体の位置を計算
            transit_positions = {}
            for planet in transit_planets:
                if planet in PLANETS:
                    pos, retflag = swe.calc_ut(jd_ut, PLANETS[planet], swe.FLG_SPEED)
                    transit_positions[planet] = {
                        'longitude': pos[0],
                        'speed': pos[3],
                    }
            
            # 重要なアスペクトをチェック
            for t_planet, t_data in transit_positions.items():
                for n_planet, n_data in natal_positions.items():
                    if n_planet not in natal_key_points:
                        continue
                        
                    # 天体間の角度差を計算
                    angle_diff = deg_diff(t_data['longitude'], n_data['longitude'])
                    
                    # 重要なアスペクトに近いかチェック
                    for aspect_angle, aspect_desc in important_aspects.items():
                        # アスペクトのオーブ（許容誤差範囲）
                        orb = 2.0 if t_planet in ['Jupiter', 'Saturn'] else 1.0
                        
                        if abs(angle_diff - aspect_angle) <= orb:
                            # イベントキーを作成
                            event_key = (t_planet, n_planet, aspect_angle)
                            
                            # イベントの説明を取得
                            if event_key in event_types:
                                event_desc = event_types[event_key]
                                
                                # 強度計算（オーブが小さいほど強い）
                                intensity = 100 - (abs(angle_diff - aspect_angle) / orb * 100)
                                intensity = round(min(intensity, 100), 1)
                                
                                # 「逆行時は効果が強くなる」などの特別ルール
                                if t_data['speed'] < 0:  # 逆行中
                                    intensity *= 1.2
                                    event_desc += "（逆行中のため効果が強調されます）"
                                
                                # イベントを追加
                                event_date = f"{check_year}年{month}月"
                                life_events.append({
                                    'date': event_date,
                                    'transit_planet': t_planet,
                                    'transit_planet_jp': PLANET_NAMES_JP.get(t_planet, t_planet),
                                    'natal_planet': n_planet,
                                    'natal_planet_jp': PLANET_NAMES_JP.get(n_planet, n_planet),
                                    'aspect_type': list(important_aspects.keys()).index(aspect_angle),
                                    'aspect_desc': aspect_desc,
                                    'event_desc': event_desc,
                                    'intensity': intensity,
                                })
    
    # イベントを日付順、強度順にソート
    life_events.sort(key=lambda x: (x['date'], -x['intensity']))
    
    return life_events 