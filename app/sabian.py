import json
import os

def load_sabian_symbols():
    """サビアンシンボルデータの読み込み（0〜359度のstrキーで返す）"""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'sabian_symbols.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    symbols = {}
    zodiac_signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    for i, sign in enumerate(zodiac_signs):
        for deg_str, symbol_text in raw.get(sign, {}).items():
            deg = int(deg_str)
            abs_deg = i * 30 + (deg - 1)  # 0〜359度
            symbols[str(abs_deg)] = {
                'symbol': symbol_text,
                'interpretation': symbol_text  # 仮：interpretationも同じ値を入れる
            }
    return symbols

def get_sabian_symbol(degree):
    """指定された度数に対応するサビアンシンボルを取得"""
    symbols = load_sabian_symbols()
    # 度数を0〜359の範囲に正規化
    degree = degree % 360
    # 度数に対応するサビアンシンボルを返す
    return symbols.get(str(degree), None)

def get_interpretation(symbol):
    """サビアンシンボルの解釈を取得"""
    symbols = load_sabian_symbols()
    # symbolがdictの場合はそのままinterpretationを返す
    if isinstance(symbol, dict):
        return symbol.get('interpretation', None)
    # 文字列の場合は一致するものを探す
    for v in symbols.values():
        if v.get('symbol') == symbol:
            return v.get('interpretation', None)
    return None 