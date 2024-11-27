import requests
from bs4 import BeautifulSoup
import traceback
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

class BaseScraper:
    @staticmethod
    def get_soup(url, headers=None):
        """
        URLからBeautifulSoupオブジェクトを取得する
        
        Args:
            url (str): スクレイピング対象のURL
            headers (dict): リクエストヘッダー
            
        Returns:
            BeautifulSoup: パースされたHTML
            エラーの場合はNone
        """
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except Exception as e:
            error_details = traceback.format_exc()
            print_and_logging(f"スクレイピング中にエラーが発生しました: {str(e)}\n{error_details}")
            return None

    @staticmethod
    def safe_select_text(soup, selector, default=None):
        """
        セレクタを使用して要素のテキストを安全に取得する
        
        Args:
            soup (BeautifulSoup): BeautifulSoupオブジェクト
            selector (str): CSSセレクタ
            default: 取得失敗時のデフォルト値
            
        Returns:
            str: 取得したテキスト、失敗時はdefault
        """
        try:
            element = soup.select_one(selector)
            return element.text.strip() if element else default
        except AttributeError:
            return default
