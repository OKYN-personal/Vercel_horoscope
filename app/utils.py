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