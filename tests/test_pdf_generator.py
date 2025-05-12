import unittest
import os
from datetime import datetime
from app.pdf_generator import generate_horoscope_pdf, render_horoscope_template
from app import create_app

class TestPDFGenerator(unittest.TestCase):
    def setUp(self):
        # Flaskアプリの作成
        self.app = create_app()
        # テスト用のデータ
        self.test_data = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00',
            'birth_place': '東京',
            'natal': {
                'positions': {
                    'Sun': {'longitude': 0, 'latitude': 0, 'distance': 1},
                    'Moon': {'longitude': 90, 'latitude': 0, 'distance': 1}
                },
                'aspects': [
                    {'planet1': 'Sun', 'planet2': 'Moon', 'aspect': 'Square'}
                ],
                'sabian': {
                    'Sun': {'symbol': 'テストシンボル1', 'interpretation': 'テスト解釈1'},
                    'Moon': {'symbol': 'テストシンボル2', 'interpretation': 'テスト解釈2'}
                }
            }
        }
        
        # 出力ディレクトリの設定
        self.output_dir = 'static/pdfs'
        os.makedirs(self.output_dir, exist_ok=True)

    def test_generate_horoscope_pdf(self):
        """PDF生成のテスト"""
        with self.app.app_context():
            # PDFの生成
            filename = generate_horoscope_pdf(self.test_data, self.output_dir)
            
            # 基本的な検証
            self.assertIsNotNone(filename)
            self.assertIsInstance(filename, str)
            self.assertTrue(filename.endswith('.pdf'))
            
            # ファイルの存在確認
            filepath = os.path.join(self.output_dir, filename)
            self.assertTrue(os.path.exists(filepath))
            
            # ファイルサイズの確認
            self.assertTrue(os.path.getsize(filepath) > 0)
            
            # テスト後にファイルを削除
            os.remove(filepath)

    def test_render_horoscope_template(self):
        """テンプレートレンダリングのテスト"""
        with self.app.app_context():
            # テンプレートのレンダリング
            html = render_horoscope_template(self.test_data)
            
            # 基本的な検証
            self.assertIsNotNone(html)
            self.assertIsInstance(html, str)
            
            # 必要な要素が含まれているか
            self.assertIn('ホロスコープ解釈', html)
            self.assertIn('1990-01-01', html)
            self.assertIn('12:00', html)
            self.assertIn('東京', html)
            self.assertIn('テストシンボル1', html)
            self.assertIn('テスト解釈1', html)

    def tearDown(self):
        # テストで作成したPDFファイルの削除
        for file in os.listdir(self.output_dir):
            if file.endswith('.pdf'):
                os.remove(os.path.join(self.output_dir, file))

if __name__ == '__main__':
    unittest.main() 