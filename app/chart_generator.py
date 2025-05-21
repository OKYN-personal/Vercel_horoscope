import math

# 定数定義
SIGN_GLYPHS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
PLANET_GLYPHS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
    'Asc': 'Asc', 'MC': 'MC'
}
# アスペクトの色とスタイル定義 (例)
ASPECT_COLORS = {
    'conjunction': 'red', 'sextile': 'blue', 'square': 'red',
    'trine': 'blue', 'opposition': 'red'
}
ASPECT_STYLES = {
    'conjunction': 'stroke-dasharray="4, 2"',
    # 他は実線 (デフォルト)
}

def deg_to_rad(deg):
    """度をラジアンに変換 (0度を右方向 = 3時の方向とする)"""
    # SVGの座標系ではy軸が下向きなので、数学的な角度と合わせるために調整
    # 0度（牡羊座0度）を左端（9時の方向）にする場合は、180度を加えるか、cos/sinの計算を調整
    # ここでは一般的な数学座標 (右が0度、上が90度) で計算し、後でSVG内で回転させる方法も考える
    # -> 0度をチャートの右端 (3時の方向) とし、反時計回りに角度が増加すると仮定
    #    チャートのASC (左端=9時の方向) は 180度に対応
    return math.radians(-deg + 90) # Y軸上向き、反時計回りを正とする数学座標系用

def polar_to_cartesian(cx, cy, radius, angle_degrees):
    """極座標をデカルト座標に変換 (SVG座標系用: 0度が右、角度は反時計回り、Y軸は下向き)"""
    angle_radians = math.radians(angle_degrees)
    x = cx + radius * math.cos(angle_radians)
    y = cy + radius * math.sin(angle_radians) # Y軸下向きに対応
    return x, y

def normalize_angle(angle):
    """角度を0-360の範囲に正規化"""
    return angle % 360

def mid_angle(angle1, angle2):
    """2つの角度の中間角度を計算 (0/360度を跨ぐ場合も考慮)"""
    diff = normalize_angle(angle2 - angle1)
    return normalize_angle(angle1 + diff / 2)

def generate_chart_svg(planets_data, cusps_data, aspects_data, chart_info_data):
    """ホロスコープチャートのSVG文字列を生成する"""
    width = 600
    height = 600
    cx = width / 2
    cy = height / 2
    radius_outer = min(cx, cy) - 10
    radius_sign_ring = radius_outer - 15
    radius_sign_symbol = radius_outer - 35
    radius_house_cusp = radius_outer - 50
    radius_house_number = radius_house_cusp - 40 # ハウス番号の半径を調整
    radius_planet_ring = radius_house_cusp - 60
    radius_aspect_inner = radius_planet_ring - 60

    # ASCの経度を取得 (存在しない場合のフォールバックも考慮)
    asc_longitude = chart_info_data.get('asc_longitude')
    if asc_longitude is None:
        asc_longitude = planets_data.get('Asc', {}).get('longitude', 0) # フォールバック

    # チャートの回転角度 (ASCを左端=180度にする)
    # SVGの rotate は時計回りが正。度数も時計回りに増加する。
    # SVG座標系の0度は右(3時)。ASCを左(9時=180度)にするための回転角。
    # 黄経 (反時計回り、牡羊座0度が0度) -> SVG角度 (時計回り、3時が0度)
    # 座標系の変換と回転を同時に行うのは複雑なので、座標を計算してから全体を回転させる。
    # まず黄経ベース (0度=右、反時計回り) で座標計算し、最後に全体を回転させる。
    # ASCが左 (180度) になるようにするには、(180 - asc_longitude) 度回転させる。
    rotation_angle = 180 - asc_longitude # ASCを左端 (9時の方向、SVGの180度) にする

    svg = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '<style>',
        '  .sign-glyph { font-size: 20px; text-anchor: middle; dominant-baseline: middle; }',
        '  .house-number { font-size: 16px; text-anchor: middle; dominant-baseline: middle; fill: #555; }',
        '  .planet-glyph { font-size: 18px; text-anchor: middle; dominant-baseline: central; fill: #00008B; }', # DarkBlue
        '  .planet-degree { font-size: 10px; text-anchor: middle; dominant-baseline: hanging; fill: #444; }',
        '  .asc-mc-label { font-size: 14px; font-weight: bold; text-anchor: middle; dominant-baseline: middle; }',
        '  .sign-line { stroke: #ccc; stroke-width: 1; }',
        '  .house-line { stroke: #aaa; stroke-width: 1; }',
        '  .asc-mc-line { stroke: #333; stroke-width: 2; }',
        '  .aspect-line { stroke-width: 1; fill: none; }',
        f'  .aspect-conjunction {{ stroke: {ASPECT_COLORS["conjunction"]}; stroke-dasharray: 4, 2; }}',
        f'  .aspect-sextile {{ stroke: {ASPECT_COLORS["sextile"]}; }}',
        f'  .aspect-square {{ stroke: {ASPECT_COLORS["square"]}; }}',
        f'  .aspect-trine {{ stroke: {ASPECT_COLORS["trine"]}; }}',
        f'  .aspect-opposition {{ stroke: {ASPECT_COLORS["opposition"]}; }}',
        '</style>',
        # 全体の回転を適用 (上下反転は行わない)
        f'<g transform="rotate({rotation_angle} {cx} {cy})">'
    ]

    # 1. サインの描画 (境界線と記号)
    svg.append('<g id="signs">')
    for i in range(12):
        angle_deg = i * 30
        # サイン境界線 (通常の座標計算)
        x1, y1 = polar_to_cartesian(cx, cy, radius_house_cusp, angle_deg)
        x2, y2 = polar_to_cartesian(cx, cy, radius_outer, angle_deg)
        svg.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="sign-line" />')
        # サイン記号 (テキストなので通常座標)
        angle_symbol_deg = angle_deg + 15 # 各サインの中間
        x_sign, y_sign = polar_to_cartesian(cx, cy, radius_sign_symbol, angle_symbol_deg)
        # 回転の打ち消しのみ
        orient_transform = f"rotate({-rotation_angle} {x_sign} {y_sign})"
        svg.append(f'  <text x="{x_sign}" y="{y_sign}" class="sign-glyph" transform="{orient_transform}">{SIGN_GLYPHS[i]}</text>')
    svg.append('</g>')

    # 2. ハウスの描画 (カスプ線と番号)
    svg.append('<g id="houses">')
    cusps_positions = {} # ハウス番号とカスプ座標を保持
    for i in range(12):
        cusp_angle_deg = cusps_data[i] # cusps_data は [1ハウス始点, 2ハウス始点, ...]
        # カスプ線 (通常の座標計算)
        # x1, y1 = polar_to_cartesian(cx, cy, radius_aspect_inner, cusp_angle_deg) # 中心から引かない場合
        x1, y1 = cx, cy # 中心から引く
        x2, y2 = polar_to_cartesian(cx, cy, radius_house_cusp, cusp_angle_deg)
        # ASCとMCの線は太くする
        line_class = 'house-line'
        if i == 0: line_class = 'asc-mc-line' # 1ハウス始点 = ASC
        elif i == 9: line_class = 'asc-mc-line' # 10ハウス始点 = MC

        svg.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{line_class}" />')
        cusps_positions[i+1] = (x2, y2) # カスプの座標を保存 (線の終点)

        # ハウス番号の描画 (テキストなので通常座標)
        cusp_next_angle_deg = cusps_data[(i + 1) % 12]
        house_mid_deg = mid_angle(cusp_angle_deg, cusp_next_angle_deg)
        x_num, y_num = polar_to_cartesian(cx, cy, radius_house_number, house_mid_deg)
        # 回転の打ち消しのみ
        orient_transform = f"rotate({-rotation_angle} {x_num} {y_num})"
        svg.append(f'  <text x="{x_num}" y="{y_num}" class="house-number" transform="{orient_transform}">{i+1}</text>')
    svg.append('</g>')

    # 3. アスペクト線の描画 (天体より先に描画して重なり順を調整)
    svg.append('<g id="aspects">')
    if aspects_data:
        # 天体の座標を事前に計算しておく (アスペクト線用、通常座標)
        planet_coords = {}
        for planet, data in planets_data.items():
            if planet not in ['Asc', 'MC']: # Asc/MC自体は線で結ばない
                angle_deg = data['longitude']
                # アスペクト線描画用に通常座標を計算
                planet_coords[planet] = polar_to_cartesian(cx, cy, radius_planet_ring, angle_deg)

        drawn_aspects = set() # 重複描画防止 (例: Sun-MoonとMoon-Sun)
        for aspect in aspects_data:
            p1 = aspect['planet1']
            p2 = aspect['planet2']
            aspect_type = aspect['aspect_type'].lower() # 小文字に正規化

            # Asc/MC を含むアスペクトは描画しない場合 (または特別扱いする場合)
            if p1 in ['Asc', 'MC'] or p2 in ['Asc', 'MC']: continue

            pair_key = tuple(sorted((p1, p2))) # (Sun, Moon) のキー
            if pair_key in drawn_aspects:
                 continue

            if p1 in planet_coords and p2 in planet_coords and aspect_type in ASPECT_COLORS:
                x1, y1 = planet_coords[p1] # 通常座標を使用
                x2, y2 = planet_coords[p2] # 通常座標を使用
                color_class = f"aspect-{aspect_type}"
                style = ASPECT_STYLES.get(aspect_type, '') # 点線などのスタイル
                svg.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="aspect-line {color_class}" {style} />')
                drawn_aspects.add(pair_key)

    svg.append('</g>')

    # 4. 天体の描画 (記号と度数)
    svg.append('<g id="planets">')
    # 描画位置が近い場合に少しずらすためのオフセット管理
    drawn_angles = {}
    offset_increment = 8 # ずらす角度 (度数)
    radius_offset_increment = 15 # ずらす半径

    # 描画順序を定義すると重なりを制御しやすい (例: 速度の遅いものから)
    planet_order = ['Pluto', 'Neptune', 'Uranus', 'Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
    planets_to_draw = [p for p in planet_order if p in planets_data and p not in ['Asc', 'MC']]
    # リストに含まれない他の天体も追加 (感受点など)
    planets_to_draw.extend([p for p in planets_data if p not in planets_to_draw and p not in ['Asc', 'MC']])

    for planet in planets_to_draw:
        data = planets_data[planet]
        angle_deg = data['longitude']
        base_radius = radius_planet_ring

        # 角度が近い天体の位置を少しずらす
        angle_key = round(normalize_angle(angle_deg) / offset_increment) # 角度をグループ化
        offset_count = drawn_angles.get(angle_key, 0)
        current_radius = base_radius - (offset_count * radius_offset_increment)
        drawn_angles[angle_key] = offset_count + 1

        # 天体記号と度数の座標計算 (テキストなので通常座標)
        x_planet, y_planet = polar_to_cartesian(cx, cy, current_radius, angle_deg)

        glyph = data.get('glyph', PLANET_GLYPHS.get(planet, '?'))
        full_degree_text = data.get('degree_plain', '') # 'degree_plain' を直接使用

        # 度数表示の座標を少し外側に調整 (通常座標)
        text_offset_radius = 18
        x_deg_text, y_deg_text = polar_to_cartesian(cx, cy, current_radius + text_offset_radius, angle_deg)

        # 天体記号と度数をグループ化し、それぞれに回転打ち消しtransformを適用
        # グループ全体で回転打ち消しを適用し、その中で相対的に配置する方がシンプルかも
        group_transform = f"rotate({-rotation_angle} {x_planet} {y_planet})" # 天体記号の位置を基準に回転打ち消し
        
        # 度数テキストは、天体記号からの相対位置ではなく、絶対座標で計算し、個別に回転打ち消し
        degree_orient_transform = f"rotate({-rotation_angle} {x_deg_text} {y_deg_text})"

        svg.append(f'  <text x="{x_planet}" y="{y_planet}" class="planet-glyph" transform="{group_transform}">{glyph}</text>')
        svg.append(f'  <text x="{x_deg_text}" y="{y_deg_text}" class="planet-degree" transform="{degree_orient_transform}">{full_degree_text}</text>')

    svg.append('</g>')

    # 5. ASC/MC ラベルの描画
    svg.append('<g id="asc-mc-labels">')
    # ASC ラベル (1ハウス始点の外側)
    # ASCラベル座標 (テキストなので通常座標)
    x_label_asc, y_label_asc = polar_to_cartesian(cx, cy, radius_house_cusp + 10, asc_longitude)
    # 回転の打ち消しのみ
    orient_transform_asc = f"rotate({-rotation_angle} {x_label_asc} {y_label_asc})"
    svg.append(f'  <text x="{x_label_asc}" y="{y_label_asc}" class="asc-mc-label" transform="{orient_transform_asc}">Asc</text>')

    # MC ラベル (10ハウス始点の外側)
    mc_longitude = chart_info_data.get('mc_longitude')
    if mc_longitude is not None:
        # MCラベル座標 (テキストなので通常座標)
        x_label_mc, y_label_mc = polar_to_cartesian(cx, cy, radius_house_cusp + 10, mc_longitude)
        # 回転の打ち消しのみ
        orient_transform_mc = f"rotate({-rotation_angle} {x_label_mc} {y_label_mc})"
        svg.append(f'  <text x="{x_label_mc}" y="{y_label_mc}" class="asc-mc-label" transform="{orient_transform_mc}">MC</text>')
    svg.append('</g>')

    # 閉じる
    svg.append('</g>') # Closing rotation group
    svg.append('</svg>')

    return '\n'.join(svg)

# テスト用 (直接実行された場合)
if __name__ == '__main__':
    # ダミーデータ
    dummy_positions = {
        'Sun': {'longitude': 15.5, 'glyph': '☉', 'degree_plain': '牡羊15.5'},
        'Moon': {'longitude': 95.2, 'glyph': '☽', 'degree_plain': '蟹5.2'},
        'Mercury': {'longitude': 5.1, 'glyph': '☿', 'degree_plain': '牡羊5.1'},
        'Venus': {'longitude': 350.8, 'glyph': '♀', 'degree_plain': '魚20.8'},
        'Mars': {'longitude': 128.3, 'glyph': '♂', 'degree_plain': '獅子8.3'},
        'Jupiter': {'longitude': 245.0, 'glyph': '♃', 'degree_plain': '射手5.0'},
        'Saturn': {'longitude': 272.1, 'glyph': '♄', 'degree_plain': '山羊2.1'},
        'Uranus': {'longitude': 66.9, 'glyph': '♅', 'degree_plain': '双子6.9'},
        'Neptune': {'longitude': 213.4, 'glyph': '♆', 'degree_plain': '天秤3.4'},
        'Pluto': {'longitude': 188.7, 'glyph': '♇', 'degree_plain': '天秤8.7'},
        'Asc': {'longitude': 190.0, 'glyph': 'Asc', 'degree_plain': '天秤10.0'}, # Asc/MCにもdegree_plainを追加
        'MC': {'longitude': 280.0, 'glyph': 'MC', 'degree_plain': '山羊10.0'}
    }
    dummy_cusps = [
        190.0, 225.0, 255.0, 280.0, 310.0, 345.0,
        10.0, 45.0, 75.0, 100.0, 130.0, 165.0
    ]
    dummy_aspects = [
        {'planet1': 'Sun', 'planet2': 'Moon', 'aspect_type': 'square', 'orb': 0.3},
        {'planet1': 'Mercury', 'planet2': 'Venus', 'aspect_type': 'sextile', 'orb': 1.1},
        {'planet1': 'Mars', 'planet2': 'Jupiter', 'aspect_type': 'trine', 'orb': 2.7},
        {'planet1': 'Sun', 'planet2': 'Saturn', 'aspect_type': 'opposition', 'orb': 0.1}
    ]
    dummy_chart_info = {
        'asc_longitude': 190.0,
        'mc_longitude': 280.0
    }

    generated_svg = generate_chart_svg(dummy_positions, dummy_cusps, dummy_aspects, dummy_chart_info)

    # ファイルに保存して確認
    with open("test_chart.svg", "w", encoding="utf-8") as f:
        f.write(generated_svg)
    print("Saved to test_chart.svg") 