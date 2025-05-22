from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """
    星座をモチーフにしたシンプルなアイコンを生成する
    
    Args:
        size: アイコンのサイズ（幅と高さが同じ正方形）
        output_path: 出力ファイルのパス
    """
    # キャンバスを作成（透明背景）
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # 青いグラデーション背景を作成
    for y in range(size):
        # 上から下へのグラデーション
        r = int(52 * (1 - y/size))  # 青い色の赤成分
        g = int(152 * (1 - y/(2*size)) + 100)  # 青い色の緑成分
        b = int(219 * (1 - y/(3*size)) + 36)  # 青い色の青成分
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # 円の描画（背景）
    circle_size = int(size * 0.8)
    offset = (size - circle_size) // 2
    draw.ellipse(
        [(offset, offset), (offset + circle_size, offset + circle_size)],
        fill=(255, 255, 255, 230)
    )
    
    # 星座のようなドットと線を描画
    dots = [
        (size * 0.3, size * 0.3),
        (size * 0.7, size * 0.25),
        (size * 0.5, size * 0.5),
        (size * 0.25, size * 0.65),
        (size * 0.75, size * 0.7)
    ]
    
    # 点を描画
    for x, y in dots:
        dot_size = int(size * 0.05)
        x1, y1 = int(x - dot_size/2), int(y - dot_size/2)
        x2, y2 = int(x + dot_size/2), int(y + dot_size/2)
        draw.ellipse([(x1, y1), (x2, y2)], fill=(52, 152, 219))
    
    # 線を描画して星座を形成
    line_width = max(1, int(size * 0.01))
    draw.line([dots[0], dots[2]], fill=(52, 152, 219), width=line_width)
    draw.line([dots[1], dots[2]], fill=(52, 152, 219), width=line_width)
    draw.line([dots[2], dots[3]], fill=(52, 152, 219), width=line_width)
    draw.line([dots[2], dots[4]], fill=(52, 152, 219), width=line_width)
    
    # 画像を保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    icon.save(output_path)
    print(f"アイコンを生成しました: {output_path}")

if __name__ == "__main__":
    # 異なるサイズのアイコンを生成
    create_icon(192, "static/icons/icon-192x192.png")
    create_icon(512, "static/icons/icon-512x512.png")
    print("すべてのアイコンが生成されました") 