from .index import app

def handler(event, context):
    """Vercelのサーバーレス関数用ハンドラ"""
    return { "body": app }
