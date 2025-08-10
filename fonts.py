import platform
import os
from pathlib import Path

def get_japanese_font_path():
    """
    システムに応じた日本語フォントのパスを取得
    """
    # ユーザーが提供したフォントファイルを優先的に使用
    current_dir = Path(__file__).parent
    user_font_path = current_dir / "NotoSansJP-VariableFont_wght.ttf"
    
    if user_font_path.exists():
        return str(user_font_path)
    
    system = platform.system()
    
    if system == "Windows":
        # Windows用の日本語フォント
        font_paths = [
            "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic
            "C:/Windows/Fonts/yu Gothic.ttc",  # Yu Gothic
            "C:/Windows/Fonts/meiryo.ttc",     # Meiryo
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
                
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/PingFang.ttc",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
                
    elif system == "Linux":
        font_paths = [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
    
    # デフォルトフォント（日本語非対応の可能性あり）
    return None

def get_font_family():
    """
    システムに応じたフォントファミリーを取得
    """
    # ユーザーが提供したフォントファイルが存在する場合は、そのフォントファミリーを返す
    current_dir = Path(__file__).parent
    user_font_path = current_dir / "NotoSansJP-VariableFont_wght.ttf"
    
    if user_font_path.exists():
        return "Noto Sans JP, sans-serif"
    
    system = platform.system()
    
    if system == "Windows":
        return "MS Gothic, Yu Gothic, Meiryo, sans-serif"
    elif system == "Darwin":  # macOS
        return "Hiragino Kaku Gothic ProN, Hiragino Sans, sans-serif"
    elif system == "Linux":
        return "Noto Sans CJK JP, DejaVu Sans, sans-serif"
    else:
        return "sans-serif"

# フォント設定のテスト
if __name__ == "__main__":
    font_path = get_japanese_font_path()
    font_family = get_font_family()
    
    print(f"システム: {platform.system()}")
    print(f"フォントパス: {font_path}")
    print(f"フォントファミリー: {font_family}")
    
    if font_path and os.path.exists(font_path):
        print("✅ 日本語フォントが見つかりました")
    else:
        print("⚠️ 日本語フォントが見つかりませんでした")
