import unittest
from datetime import datetime, date, time
from app.horoscope import calculate_natal_chart, calculate_transit, calculate_aspects

class TestHoroscope(unittest.TestCase):
    def setUp(self):
        # テスト用の日時データ
        self.birth_date = date(1990, 1, 1)
        self.birth_time = time(12, 0)
        self.birth_place = "東京"
        self.transit_date = datetime(2024, 1, 1, 12, 0)

    def test_calculate_natal_chart(self):
        """ネイタルチャート計算のテスト"""
        positions = calculate_natal_chart(self.birth_date, self.birth_time, self.birth_place)
        
        # 基本的な検証
        self.assertIsNotNone(positions)
        self.assertIsInstance(positions, dict)
        
        # 必要な天体が含まれているか
        required_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for planet in required_planets:
            self.assertIn(planet, positions)
            
        # 各天体の位置データの形式を確認
        for planet, pos in positions.items():
            self.assertIn('longitude', pos)
            self.assertIn('latitude', pos)
            self.assertIn('distance', pos)
            
            # 値の範囲チェック
            self.assertTrue(0 <= pos['longitude'] < 360)
            self.assertTrue(-90 <= pos['latitude'] <= 90)
            self.assertTrue(pos['distance'] > 0)

    def test_calculate_transit(self):
        """トランジット計算のテスト"""
        positions = calculate_transit(self.transit_date, self.birth_date, self.birth_time, self.birth_place)
        
        # 基本的な検証
        self.assertIsNotNone(positions)
        self.assertIsInstance(positions, dict)
        
        # 必要な天体が含まれているか
        required_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for planet in required_planets:
            self.assertIn(planet, positions)
            
        # 各天体の位置データの形式を確認
        for planet, pos in positions.items():
            self.assertIn('longitude', pos)
            self.assertIn('latitude', pos)
            self.assertIn('distance', pos)
            
            # 値の範囲チェック
            self.assertTrue(0 <= pos['longitude'] < 360)
            self.assertTrue(-90 <= pos['latitude'] <= 90)
            self.assertTrue(pos['distance'] > 0)

    def test_calculate_aspects(self):
        """アスペクト計算のテスト"""
        # テスト用の位置データ
        pos1 = {'longitude': 0, 'latitude': 0, 'distance': 1}
        pos2 = {'longitude': 60, 'latitude': 0, 'distance': 1}
        
        # アスペクトの計算
        aspect = calculate_aspects(pos1, pos2)
        
        # 基本的な検証
        self.assertIsNotNone(aspect)
        self.assertEqual(aspect, 'Sextile')  # 60度のアスペクト

if __name__ == '__main__':
    unittest.main() 