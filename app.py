from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

# ホロスコープ計算機能のダミー関数
def calculate_horoscope(birth_date, birth_time, latitude, longitude):
    # 実際のホロスコープ計算はここに実装します
    # 現在はダミーデータを返します
    return {
        "sun_sign": "牡羊座",
        "moon_sign": "蟹座",
        "ascendant": "射手座",
        "planets": [
            {"name": "太陽", "sign": "牡羊座", "degree": "15°30'"},
            {"name": "月", "sign": "蟹座", "degree": "23°45'"},
            {"name": "水星", "sign": "牡牛座", "degree": "2°15'"},
            {"name": "金星", "sign": "魚座", "degree": "28°10'"},
            {"name": "火星", "sign": "山羊座", "degree": "10°05'"}
        ],
        "aspects": [
            {"point1": "太陽", "point2": "月", "type": "スクエア", "orb": "1.2°"},
            {"point1": "月", "point2": "火星", "type": "トライン", "orb": "0.5°"},
            {"point1": "水星", "point2": "金星", "type": "セクスタイル", "orb": "2.1°"}
        ]
    }

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        birth_date = data.get('birthDate')
        birth_time = data.get('birthTime')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # バリデーション
        if not all([birth_date, birth_time, latitude, longitude]):
            return jsonify({"error": "すべてのフィールドを入力してください"}), 400
        
        # ホロスコープを計算
        result = calculate_horoscope(birth_date, birth_time, latitude, longitude)
        
        # 結果を返す
        return jsonify({
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/js/sw.js')
def service_worker():
    return send_from_directory('static/js', 'sw.js')

# 404エラーハンドラー
@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory('static', 'offline.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 