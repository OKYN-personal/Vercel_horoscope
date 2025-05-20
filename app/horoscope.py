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
    'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO
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
    'Asc': 'Asc', 'MC': 'MC'
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
    'True Node': 'ﾄﾞﾗｺﾞﾝﾍｯﾄﾞ',
}

# 予測などで使用する主要な天体リスト
PLANETS_FOR_FORECAST = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

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
        sign_jp_calc, sign_degree_within_sign = get_sign(pos[0]) # サイン名とサイン内度数を取得
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
        'used_timezone_offset': used_timezone_offset # 実際に使われたオフセットも返す
    }

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
        # デフォルトオーブ (適宜調整)
        orb_degrees = {
            'Conjunction': 10, 'Opposition': 10, 'Trine': 8, 'Square': 8,
            'Sextile': 6, 'Inconjunct': 2, 'Semisextile': 2, 'Quintile': 2, 'BiQuintile': 2
        }

    aspects = []
    planets1 = list(positions1.keys())

    if positions2 is None: # ネイタルチャート内のアスペクト計算
        # 同じ天体ペアを計算しないように組み合わせを生成
        for i in range(len(planets1)):
            for j in range(i + 1, len(planets1)):
                p1_name = planets1[i]
                p2_name = planets1[j]
                p1_lon = positions1[p1_name]['longitude']
                p2_lon = positions1[p2_name]['longitude']

                # 主要なアスペクトをチェック
                for aspect_name, aspect_angle in aspect_types.items():
                    orb = orb_degrees.get(aspect_name, 0) # 定義されてないアスペクトはオーブ0
                    diff = abs(p1_lon - p2_lon)
                    angle_diff = min(diff, 360 - diff) # 0-180度の角度差

                    if abs(angle_diff - aspect_angle) <= orb:
                        aspects.append({
                            'planet1': p1_name,
                            'planet2': p2_name,
                            'aspect_type': aspect_name,
                            'orb': round(abs(angle_diff - aspect_angle), 2),
                            'aspect_glyph': get_aspect_glyph(aspect_name),
                            'planet1_glyph': get_planet_glyph(p1_name),
                            'planet2_glyph': get_planet_glyph(p2_name),
                            'planet1_jp': PLANET_NAMES_JP.get(p1_name, p1_name),
                            'planet2_jp': PLANET_NAMES_JP.get(p2_name, p2_name)
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

                p1_lon = positions1[p1_name]['longitude']
                p2_lon = positions2[p2_name]['longitude']

                for aspect_name, aspect_angle in aspect_types.items():
                    orb = orb_degrees.get(aspect_name, 0)
                    diff = abs(p1_lon - p2_lon)
                    angle_diff = min(diff, 360 - diff)

                    if abs(angle_diff - aspect_angle) <= orb:
                        aspects.append({
                            'planet1': p1_name, # Transit Planet
                            'planet2': p2_name, # Natal Planet
                            'aspect_type': aspect_name,
                            'orb': round(abs(angle_diff - aspect_angle), 2),
                            'aspect_glyph': get_aspect_glyph(aspect_name),
                            'planet1_glyph': get_planet_glyph(p1_name),
                            'planet2_glyph': get_planet_glyph(p2_name),
                            'planet1_jp': PLANET_NAMES_JP.get(p1_name, p1_name), # Transit 日本語名
                            'planet2_jp': PLANET_NAMES_JP.get(p2_name, p2_name)  # Natal 日本語名
                        })
                        break

    # アスペクトをオーブの小ささ順、または特定の順序でソート（任意）
    aspects.sort(key=lambda x: x['orb'])

    return aspects

# アスペクトグリッド生成関数 (必要であれば追加)
def generate_aspect_grid(aspects, planets_order=None):
    if planets_order is None:
        planets_order = list(PLANETS.keys()) + list(POINTS.keys())

    grid = {p1: {p2: "" for p2 in planets_order} for p1 in planets_order}

    for aspect in aspects:
        p1, p2 = aspect['planet1'], aspect['planet2']
        aspect_glyph = aspect['aspect_glyph'] # aspect データからグリフを取得
        if p1 in grid and p2 in grid[p1]:
             grid[p1][p2] = aspect_glyph
        if p2 in grid and p1 in grid[p2]: # 対称性を考慮
            grid[p2][p1] = aspect_glyph

    # 対角線にXを入れるなど、必要なら調整
    for p in planets_order:
        if p in grid and p in grid[p]:
            grid[p][p] = 'X'

    return {'planets': planets_order, 'grid': grid}

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
    
    swe.close()
    return event_planet_data

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

def calculate_vernal_equinox_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の春分点の各天体のサビアンシンボルを計算 (東京基準)"""
    # swe.set_ephe_path('ephe') # calculate_celestial_sabian_at_event 内で呼ばれるので不要かも
    
    # 春分点 (太陽黄経0度) のユリウス日(UT)を見つける
    jd_vernal_equinox_ut = find_solar_longitude_event_jd_ut(year, 0.0)
    
    # その瞬間の各天体のサビアン情報を計算
    vernal_equinox_data = calculate_celestial_sabian_at_event(jd_vernal_equinox_ut, f"{year}年 春分点")
    
    # swe.close() # calculate_celestial_sabian_at_event 内で呼ばれる
    return vernal_equinox_data

def calculate_summer_solstice_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の夏至点の各天体のサビアンシンボルを計算 (東京基準)"""
    jd_summer_solstice_ut = find_solar_longitude_event_jd_ut(year, 90.0)
    summer_solstice_data = calculate_celestial_sabian_at_event(jd_summer_solstice_ut, f"{year}年 夏至点")
    return summer_solstice_data

def calculate_autumnal_equinox_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の秋分点の各天体のサビアンシンボルを計算 (東京基準)"""
    jd_autumnal_equinox_ut = find_solar_longitude_event_jd_ut(year, 180.0)
    autumnal_equinox_data = calculate_celestial_sabian_at_event(jd_autumnal_equinox_ut, f"{year}年 秋分点")
    return autumnal_equinox_data

def calculate_winter_solstice_sabian(year, latitude_tokyo=35.6895, longitude_tokyo=139.6917, timezone_offset_tokyo=9.0):
    """指定された年の冬至点の各天体のサビアンシンボルを計算 (東京基準)"""
    jd_winter_solstice_ut = find_solar_longitude_event_jd_ut(year, 270.0)
    winter_solstice_data = calculate_celestial_sabian_at_event(jd_winter_solstice_ut, f"{year}年 冬至点")
    return winter_solstice_data 