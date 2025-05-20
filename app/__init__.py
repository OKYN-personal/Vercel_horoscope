from flask import Flask
import os

def create_app():
    app = Flask(__name__, template_folder="templates")
    
    # 環境変数からGoogle Maps APIキーを取得
    app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY')

    from app.routes import bp
    app.register_blueprint(bp)

    return app 