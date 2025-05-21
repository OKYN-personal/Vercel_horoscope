import json
import os
import math # 度数計算に必要
from .utils import signs # サイン名リストをインポート

def load_sabian_symbols():
    """サビアンシンボルデータをJSONファイルから読み込む"""
    # data_path = os.path.join(os.path.dirname(__file__), 'data', 'sabian_symbols.json') # 誤ったパス
    data_path = os.path.join(os.path.dirname(__file__), '..', 'sabian_symbols.json') # 正しい相対パス
    # プロジェクトルートからの絶対パスで指定する場合 (環境依存性あり)
    # data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sabian_symbols.json'))
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Sabian symbols file not found at {data_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {data_path}")
        return {}

# ロードしたデータをキャッシュ (毎回読み込まないように)
sabian_data_cache = None

def get_sabian_data():
    global sabian_data_cache
    if sabian_data_cache is None:
        sabian_data_cache = load_sabian_symbols()
    return sabian_data_cache

def get_sign_and_degree_name(longitude):
    """黄経からサイン名と度数名(1始まり)を取得"""
    longitude = longitude % 360
    sign_index = math.floor(longitude / 30)
    degree_within_sign = math.floor(longitude % 30) + 1 # サビアンは1度始まり
    sign_name = signs[sign_index] # .utilsからインポートしたリスト
    degree_name = str(degree_within_sign) # 度数名を文字列に
    return sign_name, degree_name

def get_sabian_symbol(longitude):
    """指定された黄経度数に対応するサビアンシンボル文を取得"""
    sabian_symbols = get_sabian_data()
    sign_name, degree_name = get_sign_and_degree_name(longitude)

    if sign_name in sabian_symbols and degree_name in sabian_symbols[sign_name]:
        return sabian_symbols[sign_name][degree_name]
    else:
        return f"{sign_name}{degree_name}度のサビアンシンボルは見つかりません。"

# get_interpretation 関数は不要なので削除
# def get_interpretation(symbol):
#     """サビアンシンボルの解釈を取得"""
#     symbols = load_sabian_symbols()
#     # symbolがdictの場合はそのままinterpretationを返す
#     if isinstance(symbol, dict):
#         return symbol.get('interpretation', None)
#     # 文字列の場合は一致するものを探す
#     for v in symbols.values():
#         if v.get('symbol') == symbol:
#             return v.get('interpretation', None)
#     return None 