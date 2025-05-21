# アスペクトの定数
ASPECTS = {
    'Conjunction': 0,    # 0度
    'Sextile': 60,       # 60度
    'Square': 90,        # 90度
    'Trine': 120,        # 120度
    'Opposition': 180    # 180度
}

# アスペクトの許容範囲（度）
ASPECT_ORBS = {
    'Conjunction': 8,
    'Sextile': 6,
    'Square': 8,
    'Trine': 8,
    'Opposition': 8
}

def calculate_aspects(positions):
    """
    天体間のアスペクトを計算する
    
    Args:
        positions (dict): 天体位置の情報
    
    Returns:
        list: アスペクトの情報
    """
    aspects = []
    
    # 各天体ペアのアスペクトを計算
    planets = list(positions.keys())
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            planet1 = planets[i]
            planet2 = planets[j]
            
            # 経度の差を計算
            diff = abs(positions[planet1]['longitude'] - positions[planet2]['longitude'])
            if diff > 180:
                diff = 360 - diff
            
            # 各アスペクトをチェック
            for aspect_name, aspect_angle in ASPECTS.items():
                orb = abs(diff - aspect_angle)
                if orb <= ASPECT_ORBS[aspect_name]:
                    aspects.append({
                        'planet1': planet1,
                        'planet2': planet2,
                        'aspect': aspect_name,
                        'orb': orb
                    })
    
    return aspects

def get_aspect_description(aspect):
    """
    アスペクトの説明を取得する
    
    Args:
        aspect (dict): アスペクト情報
    
    Returns:
        str: アスペクトの説明
    """
    aspect_descriptions = {
        'Conjunction': '合（0度）: 強力な結合と統合を示します。',
        'Sextile': '六分（60度）: 調和と機会を示します。',
        'Square': '四分（90度）: 緊張と課題を示します。',
        'Trine': '三分（120度）: 調和と流れを示します。',
        'Opposition': '衝（180度）: 対立とバランスを示します。'
    }
    
    return aspect_descriptions.get(aspect['aspect'], '不明なアスペクト') 