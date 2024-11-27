import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

def test_logging():
    """print_and_logging関数のテスト"""
    # 通常のinfoログ
    print_and_logging("これは情報メッセージです")
    
    # 警告ログ
    print_and_logging("これは警告メッセージです", level='warning')
    
    # エラーログ
    print_and_logging("これはエラーメッセージです", level='error')
    
    # 日本語を含むメッセージ
    print_and_logging("これは日本語を含むメッセージです 🎉")

if __name__ == "__main__":
    test_logging()
    
    # ログファイルが作成されたことを確認
    log_file = os.path.join("data", "app.log")
    if os.path.exists(log_file):
        print_and_logging("\nログファイルが正常に作成されました:", log_file)
        print_and_logging("\nログファイルの内容:")
        with open(log_file, 'r', encoding='utf-8') as f:
            print_and_logging(f.read())
