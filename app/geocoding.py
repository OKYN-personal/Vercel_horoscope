import requests
import os
from flask import current_app

def get_coordinates_from_google_maps(address, api_key=None):
    """
    Google Maps Geocoding APIを使用して住所から緯度経度を取得する
    
    Args:
        address (str): 住所または地名
        api_key (str, optional): Google Maps APIキー
        
    Returns:
        tuple: (latitude, longitude, found) - 緯度、経度、検索結果の有無
    """
    # APIキーがない場合は環境変数から取得
    if not api_key:
        api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        if not api_key:
            try:
                api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
            except RuntimeError:
                # アプリコンテキスト外で実行された場合
                pass
    
    # APIキーがない場合は処理を中止
    if not api_key:
        return None, None, False
    
    # 日本の住所を指定する場合は、地域を日本に限定
    params = {
        'address': f"{address}, Japan",
        'key': api_key
    }
    
    try:
        response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json',
            params=params
        )
        data = response.json()
        
        if data['status'] == 'OK' and data['results']:
            # 最初の結果を使用
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng'], True
        else:
            return None, None, False
    except Exception as e:
        print(f"Google Maps API呼び出しエラー: {e}")
        return None, None, False 