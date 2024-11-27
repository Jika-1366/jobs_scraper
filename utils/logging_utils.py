import os
from datetime import datetime
import logging

def setup_logger():
    """ロガーの初期設定を行う"""
    log_dir = "data"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "app.log")
    
    # ロガーの設定
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.INFO)
    
    # ファイルハンドラーの設定
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # フォーマッターの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # ハンドラーの追加（既存のハンドラーがある場合は追加しない）
    if not logger.handlers:
        logger.addHandler(file_handler)
    
    return logger

def print_and_logging(message: str, level: str = 'info'):
    """
    メッセージを表示し、ログファイルに記録する
    
    Args:
        message (str): ログメッセージ
        level (str): ログレベル（'info', 'warning', 'error', 'debug'）
    """
    logger = setup_logger()
    
    # 現在時刻を取得
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # コンソールに出力
    print(f"{current_time} - {message}")
    
    # ログレベルに応じてログを記録
    level = level.lower()
    if level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'debug':
        logger.debug(message)
    else:
        logger.info(message)
