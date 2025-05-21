#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
天文イベント通知スクリプト
毎日実行し、満月・新月・惑星逆行などのイベントを自動通知します。
crontabなどで実行するためのスクリプトです。
"""

import os
import sys
import requests
from datetime import datetime

# アプリケーションフォルダ（このスクリプトの設置場所に応じて調整してください）
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

# Flaskアプリをインポート
from app import create_app
from app.push_notifications import send_astronomical_event_notifications

def main():
    """メイン関数。天文イベントを検出して通知を送信します。"""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 天文イベント通知チェックを開始します")
    
    # アプリケーションコンテキストを作成
    app = create_app()
    with app.app_context():
        try:
            # 天文イベントを検出して通知
            results = send_astronomical_event_notifications()
            
            # 結果をログ出力
            if results:
                for result in results:
                    event = result.get('event', 'Unknown event')
                    event_result = result.get('result', {})
                    total = event_result.get('total', 0)
                    success = event_result.get('success', 0)
                    
                    print(f"イベント「{event}」の通知: {success}/{total}件成功")
            else:
                print("今日は天文イベントがありません")
                
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 天文イベント通知チェックが完了しました")
            return True
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 