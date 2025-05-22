import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
from datetime import datetime
import pytz
import time

# 基本的なFlaskアプリケーション設定
app = Flask(__name__)
CORS(app)  # CORSを有効化

# swissephのエフェメリスパスを設定
ephe_path = os.environ.get('EPHEPATH', os.path.join(os.path.dirname(__file__), 'ephe'))
swe.set_ephe_path(ephe_path)
print(f"Using ephemeris path: {ephe_path}")

# 計算結果キャッシュ（メモリ使用量抑制のため小さく保つ）
calculation_cache = {}
MAX_CACHE_SIZE = 20

# 以下からホロスコープ計算に必要な関数を定義
def calculate_julian_day(year, month, day, hour=0, minute=0, second=0):
    """与えられた日時からユリウス日を計算する"""
    return swe.julday(year, month, day, hour + minute/60.0 + second/3600.0)

def calculate_horoscope(birth_date, birth_time, latitude, longitude):
    """ホロスコープを計算する関数"""
    # キャッシュキーの作成
    cache_key = f"{birth_date}|{birth_time}|{latitude}|{longitude}"
    
    # キャッシュにあればそれを返す
    if cache_key in calculation_cache:
        return calculation_cache[cache_key]
    
    # 日時処理
    year, month, day = map(int, birth_date.split('-'))
    hour, minute = map(int, birth_time.split(':'))
    
    # ユリウス日の計算
    jd_ut = calculate_julian_day(year, month, day, hour, minute)
    
    # 惑星位置計算
    planets = {}
    for planet_id in range(0, 10):  # 0=太陽, 1=月, 2=水星...9=冥王星
        result = swe.calc_ut(jd_ut, planet_id, 0)
        position = result[0]  # 黄道上の位置
        planets[planet_id] = position[0]  # 度数を保存
    
    # ハウス計算
    houses = swe.houses(jd_ut, latitude, longitude)[0]
    
    # 結果をフォーマット
    result = {
        "planets": planets,
        "houses": houses,
        "julian_day": jd_ut
    }
    
    # キャッシュに追加（キャッシュサイズを制限）
    if len(calculation_cache) >= MAX_CACHE_SIZE:
        # 最も古いキーを削除
        oldest_key = next(iter(calculation_cache))
        calculation_cache.pop(oldest_key)
    
    calculation_cache[cache_key] = result
    return result

# APIエンドポイント
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        start_time = time.time()
        data = request.get_json()
        
        # 必要なパラメータが存在するか確認
        required_fields = ['birth_date', 'birth_time', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # ホロスコープ計算
        result = calculate_horoscope(
            data['birth_date'],
            data['birth_time'],
            float(data['latitude']),
            float(data['longitude'])
        )
        
        # 処理時間をログに出力
        print(f"Calculation took {time.time() - start_time:.2f} seconds")
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 健全性チェック
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok", 
        "service": "calculation-api",
        "cache_size": len(calculation_cache)
    }), 200

# ウォームアップ用エンドポイント（コールドスタート軽減）
@app.route('/warmup', methods=['GET'])
def warmup():
    # 基本的な計算を実行してプロセスをウォームアップ
    test_date = "2000-01-01"
    test_time = "12:00"
    test_lat = 35.6762
    test_lon = 139.6503
    
    calculate_horoscope(test_date, test_time, test_lat, test_lon)
    return jsonify({"status": "warmed up"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 