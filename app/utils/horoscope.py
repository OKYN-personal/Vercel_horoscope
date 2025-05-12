import swisseph as swe
import json
from datetime import datetime
import os

# エフェメリスファイルのパスを設定
swe.set_ephe_path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ephe'))

# 天体の定数
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO
}

# サインの定数
SIGNS = {
    0: 'Aries',
    1: 'Taurus',
    2: 'Gemini',
    3: 'Cancer',
    4: 'Leo',
    5: 'Virgo',
    6: 'Libra',
    7: 'Scorpio',
    8: 'Sagittarius',
    9: 'Capricorn',
    10: 'Aquarius',
    11: 'Pisces'
}

def calculate_planet_positions(date_time, lat, lon):
    """
    指定された日時と場所での天体位置を計算する
    
    Args:
        date_time (datetime): 計算対象の日時
        lat (float): 緯度
        lon (float): 経度
    
    Returns:
        dict: 天体位置の情報
    """
    # ユリウス日を計算
    julian_day = swe.julday(
        date_time.year,
        date_time.month,
        date_time.day,
        date_time.hour + date_time.minute/60.0
    )
    
    # 各天体の位置を計算
    positions = {}
    for planet_name, planet_id in PLANETS.items():
        # 天体位置を計算
        result = swe.calc_ut(julian_day, planet_id)
        longitude = result[0]
        
        # サインと度数を計算
        sign_num = int(longitude / 30)
        degree = longitude % 30
        
        positions[planet_name] = {
            'longitude': longitude,
            'sign': SIGNS[sign_num],
            'degree': degree,
            'sign_num': sign_num
        }
    
    return positions

def get_sabian_symbol(sign, degree):
    """
    サビアンシンボルを取得する
    
    Args:
        sign (str): サイン名
        degree (float): 度数
    
    Returns:
        str: サビアンシンボルの説明
    """
    # 度数を整数に変換（四捨五入）
    degree_int = int(round(degree))
    
    # サビアンシンボルのデータを読み込む
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sabian_symbols.json'), 'r', encoding='utf-8') as f:
        sabian_data = json.load(f)
    
    # サビアンシンボルを取得
    try:
        return sabian_data[sign][str(degree_int)]
    except KeyError:
        return f"{sign} {degree_int}度のサビアンシンボルが見つかりません" 