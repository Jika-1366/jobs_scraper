import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraping.lancers_scraper import LancersJobScraper
from utils.logging_utils import print_and_logging

def get_job_details(url: str) -> dict:
    """
    URLに基づいて適切なスクレイパーを選択し、ジョブ情報を取得する

    Args:
        url (str): スクレイピング対象のURL

    Returns:
        dict: ジョブの詳細情報を含む辞書
        取得に失敗した場合はNone
    """
    try:
        if "lancers" in url.lower():
            print_and_logging("Lancersのジョブ情報を取得します")
            return LancersJobScraper.get_job_details(url)
        else:
            print_and_logging(f"未対応のジョブサイトです: {url}")
            return None
            
    except Exception as e:
        print_and_logging(f"ジョブ情報の取得中にエラーが発生しました: {str(e)}")
        return None

def get_multiple_jobs_details(urls: list) -> list:
    """
    複数のURLからジョブ情報を取得する

    Args:
        urls (list): スクレイピング対象のURLリスト

    Returns:
        list: 各ジョブの詳細情報を含む辞書のリスト
    """
    results = []
    for url in urls:
        job_details = get_job_details(url)
        if job_details:
            results.append(job_details)
    return results
