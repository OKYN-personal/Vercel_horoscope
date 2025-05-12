import unittest
from app.sabian import load_sabian_symbols, get_sabian_symbol, get_interpretation

class TestSabian(unittest.TestCase):
    def setUp(self):
        # サビアンシンボルデータの読み込み
        self.symbols = load_sabian_symbols()

    def test_load_sabian_symbols(self):
        """サビアンシンボルデータ読み込みのテスト"""
        # 基本的な検証
        self.assertIsNotNone(self.symbols)
        self.assertIsInstance(self.symbols, dict)
        
        # データの範囲チェック
        self.assertTrue(len(self.symbols) > 0)
        
        # 各シンボルの形式を確認
        for degree, symbol in self.symbols.items():
            self.assertIsInstance(degree, str)
            self.assertIsInstance(symbol, dict)
            self.assertIn('symbol', symbol)
            self.assertIn('interpretation', symbol)

    def test_get_sabian_symbol(self):
        """サビアンシンボル取得のテスト"""
        # 正常系のテスト
        symbol = get_sabian_symbol(0)
        self.assertIsNotNone(symbol)
        self.assertIsInstance(symbol, dict)
        self.assertIn('symbol', symbol)
        self.assertIn('interpretation', symbol)
        
        # 範囲外の値のテスト
        symbol = get_sabian_symbol(360)
        self.assertIsNotNone(symbol)  # 360度は0度として扱われる
        
        # 負の値のテスト
        symbol = get_sabian_symbol(-90)
        self.assertIsNotNone(symbol)  # 負の値は正の値に変換される

    def test_get_interpretation(self):
        """サビアンシンボル解釈取得のテスト"""
        # 正常系のテスト
        interpretation = get_interpretation(self.symbols['0'])
        self.assertIsNotNone(interpretation)
        self.assertIsInstance(interpretation, str)
        
        # 存在しないシンボルのテスト
        interpretation = get_interpretation({'symbol': '存在しないシンボル'})
        self.assertIsNone(interpretation)

if __name__ == '__main__':
    unittest.main() 