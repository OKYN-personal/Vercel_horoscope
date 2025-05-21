import json
import time
from flask import current_app
from pywebpush import webpush, WebPushException
import os
from datetime import datetime, timedelta

# サブスクリプション情報を保存するインメモリストア（本番環境ではデータベースなどに置き換える）
IN_MEMORY_SUBSCRIPTIONS = []

def get_subscriptions():
    """保存されているプッシュ通知サブスクリプションを取得する"""
    global IN_MEMORY_SUBSCRIPTIONS
    
    try:
        # Vercel環境ではファイルシステムに永続的に書き込めないため、
        # データベースやKVストアの使用が推奨されますが、
        # 簡易的にインメモリストアを使用
        if os.environ.get('VERCEL_ENV'):
            return IN_MEMORY_SUBSCRIPTIONS
        
        # ローカル環境ではファイルを使用
        if os.path.exists('push_subscriptions.json'):
            with open('push_subscriptions.json', 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        current_app.logger.error(f"Error loading subscriptions: {e}")
        return []

def save_subscription(subscription_info):
    """新しいプッシュ通知サブスクリプションを保存する"""
    global IN_MEMORY_SUBSCRIPTIONS
    
    try:
        subscriptions = get_subscriptions()
        
        # すでに同じエンドポイントが登録されていないか確認
        for sub in subscriptions:
            if sub.get('endpoint') == subscription_info.get('endpoint'):
                return True  # 既存のサブスクリプションが見つかった
        
        # 新しいサブスクリプションを追加
        subscriptions.append(subscription_info)
        
        # Vercel環境ではインメモリストアに保存
        if os.environ.get('VERCEL_ENV'):
            IN_MEMORY_SUBSCRIPTIONS = subscriptions
            return True
        
        # ローカル環境ではファイルに保存
        with open('push_subscriptions.json', 'w') as f:
            json.dump(subscriptions, f)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving subscription: {e}")
        return False

def remove_subscription(endpoint):
    """プッシュ通知サブスクリプションを削除する"""
    global IN_MEMORY_SUBSCRIPTIONS
    
    try:
        subscriptions = get_subscriptions()
        new_subscriptions = [sub for sub in subscriptions if sub.get('endpoint') != endpoint]
        
        if len(subscriptions) == len(new_subscriptions):
            return False  # 削除すべきサブスクリプションが見つからなかった
        
        # Vercel環境ではインメモリストアを更新
        if os.environ.get('VERCEL_ENV'):
            IN_MEMORY_SUBSCRIPTIONS = new_subscriptions
            return True
            
        # ローカル環境ではファイルに保存
        with open('push_subscriptions.json', 'w') as f:
            json.dump(new_subscriptions, f)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error removing subscription: {e}")
        return False

def send_push_notification(subscription_info, title, message, icon=None, url=None, tag=None):
    """特定のサブスクリプションにプッシュ通知を送信する"""
    try:
        # 環境変数からVAPIDキーを取得
        vapid_private_key = current_app.config.get('VAPID_PRIVATE_KEY')
        vapid_claims = {
            "sub": "mailto:admin@horoscope-app.example.com"
        }
        
        # 通知データの準備
        data = {
            "title": title,
            "body": message,
            "timestamp": int(time.time())
        }
        
        if icon:
            data["icon"] = icon
        if url:
            data["url"] = url
        if tag:
            data["tag"] = tag
        
        # 通知を送信
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(data),
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims
        )
        
        return True
    except WebPushException as e:
        # HTTPステータスが410の場合、サブスクリプションは期限切れ
        if e.response and e.response.status_code == 410:
            remove_subscription(subscription_info.get('endpoint'))
        current_app.logger.error(f"WebPushException: {e}")
        return False
    except Exception as e:
        current_app.logger.error(f"Error sending push notification: {e}")
        return False

def broadcast_notification(title, message, icon=None, url=None, tag=None):
    """登録されているすべてのサブスクリプションに通知を送信する"""
    subscriptions = get_subscriptions()
    success_count = 0
    failed_endpoints = []
    
    for subscription in subscriptions:
        try:
            success = send_push_notification(subscription, title, message, icon, url, tag)
            if success:
                success_count += 1
            else:
                failed_endpoints.append(subscription.get('endpoint'))
        except Exception as e:
            current_app.logger.error(f"Error in broadcast_notification: {e}")
            failed_endpoints.append(subscription.get('endpoint'))
    
    # 失敗したエンドポイントを削除
    for endpoint in failed_endpoints:
        remove_subscription(endpoint)
    
    return {
        "total": len(subscriptions),
        "success": success_count,
        "failed": len(failed_endpoints)
    }

def send_astronomical_event_notifications():
    """天文イベント通知を送信する"""
    # 今日の日付
    today = datetime.now()
    events = []
    
    # 今月の満月・新月のチェック（仮の実装、実際には天文計算が必要）
    if today.day == 15:  # 仮に15日を満月とする
        events.append({
            "title": "満月のお知らせ",
            "message": f"本日は満月です。感情や潜在意識に関する洞察が得られる時期です。",
            "icon": "/static/icons/full-moon.png",
            "tag": "astronomical-event"
        })
    elif today.day == 1:  # 仮に1日を新月とする
        events.append({
            "title": "新月のお知らせ",
            "message": f"本日は新月です。新しい始まりや目標設定に適した時期です。",
            "icon": "/static/icons/new-moon.png",
            "tag": "astronomical-event"
        })
    
    # 惑星の逆行チェック（実際には天文計算が必要）
    retrogrades = [
        {"planet": "水星", "start": (3, 20), "end": (4, 12)},
        {"planet": "金星", "start": (5, 13), "end": (6, 25)},
        {"planet": "火星", "start": (9, 10), "end": (11, 15)}
    ]
    
    for r in retrogrades:
        start_date = datetime(today.year, r["start"][0], r["start"][1])
        end_date = datetime(today.year, r["end"][0], r["end"][1])
        
        # 逆行開始日のチェック
        if today.date() == start_date.date():
            events.append({
                "title": f"{r['planet']}の逆行開始",
                "message": f"本日から{r['planet']}が逆行します。{r['planet']}に関連する事柄に注意が必要です。",
                "icon": f"/static/icons/{r['planet']}-retrograde.png",
                "tag": "retrograde-start"
            })
        
        # 逆行終了日のチェック
        if today.date() == end_date.date():
            events.append({
                "title": f"{r['planet']}の逆行終了",
                "message": f"本日で{r['planet']}の逆行が終了します。徐々に通常の動きに戻ります。",
                "icon": f"/static/icons/{r['planet']}-direct.png",
                "tag": "retrograde-end"
            })
    
    # 通知を送信
    results = []
    for event in events:
        result = broadcast_notification(
            event["title"], 
            event["message"], 
            event.get("icon"), 
            None, 
            event.get("tag")
        )
        results.append({
            "event": event["title"],
            "result": result
        })
    
    return results 