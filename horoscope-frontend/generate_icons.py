import os
from PIL import Image, ImageDraw, ImageFont

def generate_pwa_icons():
    """PWA用のシンプルなアイコンを生成する"""
    try:
        # アイコン保存ディレクトリの確認
        icons_dir = os.path.join('static', 'icons')
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
            print(f"Created directory: {icons_dir}")
        
        # アイコンサイズ
        sizes = [192, 512]
        
        for size in sizes:
            # 新しいイメージの作成
            img = Image.new('RGBA', (size, size), color=(52, 152, 219, 255))  # #3498db色
            draw = ImageDraw.Draw(img)
            
            # 円を描画
            margin = size // 10
            draw.ellipse(
                [(margin, margin), (size - margin, size - margin)],
                fill=(255, 255, 255, 200)
            )
            
            # 文字を描画（可能であれば）
            try:
                # フォントサイズ
                font_size = size // 4
                # フォントロード（システムフォントを使用）
                try:
                    font = ImageFont.truetype("Arial", font_size)
                except:
                    # フォールバック
                    font = ImageFont.load_default()
                
                # テキスト描画
                text = "占星"
                text_width, text_height = draw.textsize(text, font=font)
                text_position = ((size - text_width) // 2, (size - text_height) // 2)
                draw.text(text_position, text, fill=(52, 73, 94, 255), font=font)  # #34495e色
            except Exception as e:
                print(f"Warning: Could not add text to icon: {e}")
            
            # ファイル保存
            filename = os.path.join(icons_dir, f"icon-{size}x{size}.png")
            img.save(filename)
            print(f"Generated icon: {filename}")
    
    except Exception as e:
        print(f"Error generating icons: {e}")

if __name__ == "__main__":
    generate_pwa_icons()
    print("Icon generation completed.") 