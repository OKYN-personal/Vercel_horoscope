# Zodiac signs (English)
signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Zodiac signs (Japanese)
SIGN_JP = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座"
]

# Planet glyphs
PLANET_GLYPHS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
    'Asc': 'Asc', 'MC': 'MC',
    'True Node': '☊' # Example for True Node
}

# Aspect glyphs and angles (used as aspect_types in horoscope.py)
# aspect_types in horoscope.py refers to a dict like {'Conjunction': 0, ...}
# For clarity, we'll define ASPECT_ANGLES and ASPECT_GLYPHS separately
ASPECT_ANGLES = {
    'Conjunction': 0, 'Sextile': 60, 'Square': 90, 'Trine': 120, 'Opposition': 180,
    'Inconjunct': 150, 'Semisextile': 30, 'Quintile': 72, 'BiQuintile': 144
    # Add more if needed
}

ASPECT_GLYPHS = {
    'Conjunction': '☌', 'Sextile': '∗', 'Square': '□', 'Trine': '△', 'Opposition': '☍',
    'Inconjunct': '⚻', 'Semisextile': '⚺', 'Quintile': 'Q', 'BiQuintile': 'bQ'
    # Add more if needed
}

# Helper function to get Japanese sign name from English sign name
def get_sign_jp(english_sign_name):
    try:
        index = signs.index(english_sign_name)
        return SIGN_JP[index]
    except ValueError:
        return english_sign_name # Return original if not found

# Helper function to get planet glyph
def get_planet_glyph(planet_name):
    return PLANET_GLYPHS.get(planet_name, '?')

# Helper function to get aspect glyph
def get_aspect_glyph(aspect_name):
    return ASPECT_GLYPHS.get(aspect_name, '?')

# aspect_types for direct import into horoscope.py
aspect_types = ASPECT_ANGLES

# 日本の主要都市の緯度経度データ
JAPAN_CITIES = {
    # 主要都市
    '東京': {'latitude': 35.6895, 'longitude': 139.6917},
    '大阪': {'latitude': 34.6937, 'longitude': 135.5022},
    '名古屋': {'latitude': 35.1815, 'longitude': 136.9066},
    '福岡': {'latitude': 33.5902, 'longitude': 130.4017},
    '札幌': {'latitude': 43.0618, 'longitude': 141.3545},
    '仙台': {'latitude': 38.2682, 'longitude': 140.8694},
    '広島': {'latitude': 34.3853, 'longitude': 132.4553},
    '金沢': {'latitude': 36.561049, 'longitude': 136.656631},
    '那覇': {'latitude': 26.2124, 'longitude': 127.6809},
    '横浜': {'latitude': 35.4498, 'longitude': 139.6424},
    '京都': {'latitude': 35.0116, 'longitude': 135.7681},
    '神戸': {'latitude': 34.6913, 'longitude': 135.1956},
    '埼玉': {'latitude': 35.8616, 'longitude': 139.6456},
    '千葉': {'latitude': 35.6073, 'longitude': 140.1063},
    '新潟': {'latitude': 37.9161, 'longitude': 139.0364},
    '静岡': {'latitude': 34.9756, 'longitude': 138.3827},
}

def get_city_coordinates(place_name):
    """
    地名から緯度経度を取得する関数
    
    Args:
        place_name (str): 地名（都市名や住所など）
        
    Returns:
        tuple: (latitude, longitude) または地名が見つからない場合は None
    """
    # 入力された地名に日本の都市名が含まれているか確認
    for city, coords in JAPAN_CITIES.items():
        if city in place_name:
            return coords['latitude'], coords['longitude'], True
    
    # 地名が見つからなかった場合はNoneを返す
    return None, None, False

def validate_date(date_str):
    """日付のバリデーション"""
    # TODO: 実装
    pass

def validate_time(time_str):
    """時刻のバリデーション"""
    # TODO: 実装
    pass

def validate_place(place_str):
    """場所のバリデーション"""
    # TODO: 実装
    pass 