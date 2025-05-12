from flask import Flask

def create_app():
    app = Flask(__name__, template_folder="templates")

    from app.routes import bp
    app.register_blueprint(bp)

    return app 