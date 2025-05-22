from .index import app
from flask import Response

def handler(event, context):
    """
    Vercelのサーバーレス関数用ハンドラ
    
    event: HTTPリクエスト情報
    context: 実行コンテキスト
    """
    # リクエスト情報の取得
    method = event.get('method', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # 環境変数
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': event.get('query', ''),
        'CONTENT_LENGTH': str(len(body) if body else 0),
        'HTTP': 'on',
        'SERVER_PROTOCOL': 'HTTP/1.1',
    }
    
    # ヘッダーの処理
    for header, value in headers.items():
        key = 'HTTP_' + header.upper().replace('-', '_')
        environ[key] = value
    
    # レスポンスオブジェクト
    status_code = 200
    response_headers = []
    response_body = ''
    
    # WSGIアプリケーションとして実行
    def start_response(status, headers):
        nonlocal status_code, response_headers
        status_code = int(status.split(' ')[0])
        response_headers = headers
    
    # Flaskアプリケーションの実行
    response_body = b''.join(app(environ, start_response))
    
    # 文字列に変換
    if isinstance(response_body, bytes):
        response_body = response_body.decode('utf-8')
    
    # レスポンスの構築
    return {
        'statusCode': status_code,
        'headers': dict(response_headers),
        'body': response_body
    } 