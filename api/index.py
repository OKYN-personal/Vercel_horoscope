import os
import sys
import requests
from flask import Flask, send_from_directory, request, jsonify, redirect

# 最小限のFlaskアプリを作成
app = Flask(__name__)

# 外部計算APIのURL - 環境変数から取得するか、デフォルト値を使用
CALCULATION_API = os.environ.get('CALCULATION_API', 'https://<your-render-app-name>.onrender.com')

# インデックスページリダイレクト
@app.route('/', methods=['GET'])
def index():
    return redirect('/static/index.html')

# 静的ファイルの提供
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# PWAマニフェストファイルの提供
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

# 計算APIへのプロキシ
@app.route('/calculate', methods=['POST'])
def calculate_proxy():
    try:
        # リクエストデータを外部APIに転送
        response = requests.post(f"{CALCULATION_API}/calculate", json=request.json, timeout=55)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({"error": "計算APIがタイムアウトしました。後でもう一度お試しください。"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ウォームアップエンドポイント
@app.route('/warmup', methods=['GET'])
def warmup_proxy():
    try:
        # 外部APIをウォームアップ
        response = requests.get(f"{CALCULATION_API}/warmup", timeout=10)
        return jsonify({"status": "warmed up", "api_response": response.json()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 健全性チェック
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "version": "1.0.0"}), 200

# 開発環境で実行するための条件
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 