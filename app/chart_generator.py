import math

# 定数 (必要に応じて horoscope.py と共通化)
PLANET_GLYPHS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
    'Asc': 'Asc', 'MC': 'MC'
}
SIGN_COLORS = { # サインの色分け (例)
    "火": "#FF6666", "地": "#996633", "風": "#FFFF99", "水": "#99CCFF"
}
SIGN_ELEMENTS = [ # 牡羊座から順に
    "火", "地", "風", "水", "火", "地", "風", "水", "火", "地", "風", "水"
]


def deg_to_rad(deg):
    """度をラジアンに変換 (0度を右方向 = 3時の方向とする)"""
    # SVGの座標系ではy軸が下向きなので、数学的な角度と合わせるために調整
    # 0度（牡羊座0度）を左端（9時の方向）にする場合は、180度を加えるか、cos/sinの計算を調整
    # ここでは一般的な数学座標 (右が0度、上が90度) で計算し、後でSVG内で回転させる方法も考える
    # -> 0度をチャートの右端 (3時の方向) とし、反時計回りに角度が増加すると仮定
    #    チャートのASC (左端=9時の方向) は 180度に対応
    return math.radians(-deg + 90) # Y軸上向き、反時計回りを正とする数学座標系用

def polar_to_cartesian(cx, cy, r, angle_rad):
    """極座標を直交座標に変換"""
    x = cx + r * math.cos(angle_rad)
    y = cy - r * math.sin(angle_rad) # SVGはY軸下向きなので減算
    return x, y

def generate_chart_svg(positions, cusps, width=400, height=400):
    """ホロスコープチャートのSVG文字列を生成"""
    cx, cy = width / 2, height / 2 # 中心座標
    outer_radius = min(cx, cy) * 0.9 # 外側の円の半径
    planet_radius = outer_radius * 0.8 # 天体を配置する円の半径
    house_num_radius = outer_radius * 0.6 # ハウス番号を配置する円の半径
    sign_radius = outer_radius # サイン境界を描画する円の半径
    cusp_inner_radius = outer_radius * 0.5 # カスプ線の内側半径

    svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
    svg += '<style>.planet { font-size: 14px; font-family: "Astrological Symbols", "Apple Symbols", sans-serif; } .house_num { font-size: 10px; fill: #555; text-anchor: middle; dominant-baseline: central; }</style>'

    # --- 描画要素 ---

    # 背景円 (オプション)
    # svg += f'<circle cx="{cx}" cy="{cy}" r="{outer_radius}" fill="#f0f0f0" stroke="#ccc" />'

    # サイン分割 (12サイン x 30度)
    for i in range(12):
        angle_start_deg = i * 30
        angle_end_deg = (i + 1) * 30
        angle_start_rad = deg_to_rad(angle_start_deg)
        angle_end_rad = deg_to_rad(angle_end_deg)

        # サインの背景色を描画 (扇形)
        # path で扇形を描く: M(移動) L(中心へ) A(円弧) z(閉じる)
        x_start, y_start = polar_to_cartesian(cx, cy, sign_radius, angle_start_rad)
        x_end, y_end = polar_to_cartesian(cx, cy, sign_radius, angle_end_rad)
        element = SIGN_ELEMENTS[i]
        color = SIGN_COLORS.get(element, "#eee")

        # large-arc-flag は 180度を超える円弧なら1, sweep-flag は反時計回りなら0
        # 30度の円弧なので large-arc-flag は 0
        svg += f'<path d="M {cx} {cy} L {x_start} {y_start} A {sign_radius} {sign_radius} 0 0 0 {x_end} {y_end} z" fill="{color}" stroke="#ccc" stroke-width="0.5" />'

        # サイン分割線
        # svg += f'<line x1="{cx}" y1="{cy}" x2="{x_start}" y2="{y_start}" stroke="#ccc" stroke-width="0.5" />' # 中心からの線


    # ハウスカスプ線と番号 (cusps は 0基点のリストで12個のカスプ角度が入る)
    cusps_norm = [(c % 360) for c in cusps]
    for i in range(12):
        cusp_angle_deg = cusps_norm[i]
        cusp_angle_rad = deg_to_rad(cusp_angle_deg)
        x1, y1 = polar_to_cartesian(cx, cy, cusp_inner_radius, cusp_angle_rad) # 内側の点
        x2, y2 = polar_to_cartesian(cx, cy, outer_radius, cusp_angle_rad)    # 外側の点

        # ASC (1室カスプ) と MC (10室カスプ) は太線にする
        stroke_width = 2 if i == 0 or i == 9 else 1
        stroke_color = "#333" if i == 0 or i == 9 else "#aaa"

        svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="{stroke_width}" />'

        # ハウス番号を描画 (各ハウスの中間あたりに)
        # 次のカスプとの中間角度を計算
        next_cusp_angle_deg = cusps_norm[(i + 1) % 12]
        # 角度の差を計算 (0度をまたぐ場合も考慮)
        angle_diff = (next_cusp_angle_deg - cusp_angle_deg + 360) % 360
        mid_angle_deg = (cusp_angle_deg + angle_diff / 2) % 360
        mid_angle_rad = deg_to_rad(mid_angle_deg)
        num_x, num_y = polar_to_cartesian(cx, cy, house_num_radius, mid_angle_rad)
        svg += f'<text x="{num_x}" y="{num_y}" class="house_num">{i+1}</text>'


    # 天体・感受点の配置 (positions 辞書を使用)
    for name, data in positions.items():
        if 'longitude' in data:
            angle_deg = data['longitude']
            angle_rad = deg_to_rad(angle_deg)
            p_x, p_y = polar_to_cartesian(cx, cy, planet_radius, angle_rad)
            glyph = PLANET_GLYPHS.get(name, '?')
            # 記号の色などを調整可能
            fill_color = "black"
            if name == 'Asc': fill_color = "red"
            if name == 'MC': fill_color = "blue"

            svg += f'<text x="{p_x}" y="{p_y}" class="planet" fill="{fill_color}" text-anchor="middle" dominant-baseline="central">{glyph}</text>'

    svg += '</svg>'
    return svg

# テスト用 (直接実行された場合)
if __name__ == '__main__':
    # ダミーデータ
    dummy_positions = {
        'Sun': {'longitude': 15.5, 'glyph': '☉'}, # 牡羊座15度
        'Moon': {'longitude': 95.2, 'glyph': '☽'}, # 蟹座5度
        'Mercury': {'longitude': 5.1, 'glyph': '☿'}, # 牡羊座5度
        'Venus': {'longitude': 350.8, 'glyph': '♀'}, # 魚座20度
        'Mars': {'longitude': 128.3, 'glyph': '♂'}, # 獅子座8度
        'Jupiter': {'longitude': 245.0, 'glyph': '♃'},# 射手座5度
        'Saturn': {'longitude': 272.1, 'glyph': '♄'}, # 山羊座2度
        'Uranus': {'longitude': 66.9, 'glyph': '♅'},  # 双子座6度
        'Neptune': {'longitude': 213.4, 'glyph': '♆'}, # 天秤座3度
        'Pluto': {'longitude': 188.7, 'glyph': '♇'},  # 天秤座8度
        'Asc': {'longitude': 190.0, 'glyph': 'Asc'}, # 天秤座10度
        'MC': {'longitude': 280.0, 'glyph': 'MC'}   # 山羊座10度
    }
    # ハウスカスプ (Placidusの例 - 実際は計算結果を使う)
    dummy_cusps = [
        190.0, # 1st (Asc)
        225.0, # 2nd
        255.0, # 3rd
        280.0, # 4th (IC)
        310.0, # 5th
        345.0, # 6th
        10.0,  # 7th (Desc)
        45.0,  # 8th
        75.0,  # 9th
        100.0, # 10th (MC) - ここはMCと一致するはずだが計算方法による
        130.0, # 11th
        165.0  # 12th
    ]

    generated_svg = generate_chart_svg(dummy_positions, dummy_cusps)
    # print(generated_svg) # 出力が長すぎるのでコメントアウト

    # ファイルに保存して確認
    with open("test_chart.svg", "w", encoding="utf-8") as f:
        f.write(generated_svg)
    print("Saved to test_chart.svg") 