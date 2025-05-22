import os
from PIL import Image, ImageDraw

def generate_icons():
    """PWA用のシンプルなアイコンを生成する"""
    icons_dir = os.path.join("static", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    sizes = [192, 512]
    
    for size in sizes:
        # 新しい画像を作成（青色の背景）
        img = Image.new("RGBA", (size, size), color=(52, 152, 219, 255))
        draw = ImageDraw.Draw(img)
        
        # 中心に白い円を描画
        margin = size // 10
        draw.ellipse(
            [(margin, margin), (size - margin, size - margin)],
            fill=(255, 255, 255, 220)
        )
        
        # 中心に星形を描画
        star_points = []
        center_x, center_y = size // 2, size // 2
        outer_radius = size // 3
        inner_radius = size // 6
        
        for i in range(10):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = i * 36 * (3.14159 / 180)  # 36度ずつ（360度 / 10）
            x = center_x + radius * 1.2 * (0.5 - i % 5 * 0.2)
            y = center_y + radius * (0.8 + i % 3 * 0.1)
            star_points.append((x, y))
        
        # 星形を描画
        draw.polygon(star_points, fill=(41, 128, 185, 255))
        
        # ファイル保存
        filename = os.path.join(icons_dir, f"icon-{size}x{size}.png")
        img.save(filename)
        print(f"Generated icon: {filename}")

if __name__ == "__main__":
    generate_icons()
    print("Icon generation completed.") 