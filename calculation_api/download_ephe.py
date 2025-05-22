import os
import sys
import requests
import zipfile
import io
import shutil

def download_ephemeris_files():
    """
    必要最小限のエフェメリスファイルだけをダウンロード
    """
    ephe_dir = os.environ.get('EPHEPATH', os.path.join(os.path.dirname(__file__), 'ephe'))
    
    if not os.path.exists(ephe_dir):
        os.makedirs(ephe_dir)
        print(f"Created directory: {ephe_dir}")
    
    # 必要最小限のエフェメリスファイルリスト
    # 現代のホロスコープに必要な最小限のファイルのみ
    files_to_download = [
        # 月と惑星の位置（2000年以降のデータのみ）
        'semo_18.se1',  # 月
        'sepl_18.se1',  # 惑星
    ]
    
    base_url = "https://www.astro.com/ftp/swisseph/ephe/"
    
    print("Downloading ephemeris files...")
    for file in files_to_download:
        target_path = os.path.join(ephe_dir, file)
        
        if os.path.exists(target_path):
            print(f"File already exists: {file}")
            continue
        
        try:
            print(f"Downloading {file}...")
            response = requests.get(f"{base_url}{file}", stream=True)
            
            if response.status_code == 200:
                with open(target_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print(f"Downloaded: {file}")
            else:
                print(f"Failed to download {file}: HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Error downloading {file}: {e}")
    
    # 位置計算に必要な基本的な設定ファイルを作成
    create_minimal_config_files(ephe_dir)
    
    print("Ephemeris files download completed.")

def create_minimal_config_files(ephe_dir):
    """最小限の設定ファイルを作成"""
    # 恒星データの最小設定（必要に応じて）
    with open(os.path.join(ephe_dir, "sefstars.txt"), "w") as f:
        f.write("# Minimal star data for operation\n")
        f.write("# Star name, RA, DEC\n")
        f.write("Sirius,6.7525,16.7161\n")
    
    print("Created minimal configuration files")

if __name__ == "__main__":
    download_ephemeris_files() 