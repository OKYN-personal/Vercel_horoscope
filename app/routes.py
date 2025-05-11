from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/calculate', methods=['POST'])
def calculate():
    # TODO: ホロスコープ計算ロジックの実装
    return jsonify({'message': '計算機能は現在開発中です。'}) 