import os
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    )
    
    # PWAプッシュ通知用のVAPIDキー設定
    app.config['VAPID_PRIVATE_KEY'] = os.environ.get('VAPID_PRIVATE_KEY', 
        'LS0tLS1CRUdJTiBFQyBQUklWQVRFIEtFWS0tLS0tCk1IY0NBUUVFSUhaaVRsT3BvMFdGREdEU2JjZk90bWtKMlZRd21kcm5kWlhtRENKK01zWXBvQW9HQ0NxR1NNNDkKQXdFSG9VUURRZ0FFcVZ6UFRNZnVVWkc2UlgzYjRCQWViVUtDWVhSMUVDa3FaWWRGWUR0Y3FLUTlpbzVYWXRxVwpUL3lNSnJzWk43TTFGMnJnMVdCZ1o2bGZGQnhCY0ZuT0lRPT0KLS0tLS1FTkQgRUMgUFJJVkFURSBLRVktLS0tLQ==')
    app.config['VAPID_PUBLIC_KEY'] = os.environ.get('VAPID_PUBLIC_KEY',
        'BLGrDkBXpHE1yt18jo9v7-SxDhxCQYQxqTN5rQzemDXOBEqjCpgj5MlK0JWoA8RAGg2NDcoUkXl-xY4kOrWu3QI')
    
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app 