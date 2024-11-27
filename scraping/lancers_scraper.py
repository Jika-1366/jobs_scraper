import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging
from scraping.base_scraper import BaseScraper

class LancersJobScraper(BaseScraper):
    """Lancersの案件情報をスクレイピングするクラス"""
    
    @classmethod
    def get_job_details(cls, url):
        """
        Lancers案件の詳細情報を取得する
        
        Args:
            url (str): Lancers案件のURL
            
        Returns:
            dict: 案件の詳細情報を含む辞書
            取得に失敗した場合はNone
        """
        # Lancersに負荷をかけないよう0.5秒待機
        time.sleep(0.5)
        
        print_and_logging(f"スクレイピング対象のURL: {url}")
        
        soup = cls.get_soup(url)
        if not soup:
            return None

        try:
            job_info = {}

            # タイトルの取得
            job_info['title'] = cls.safe_select_text(
                soup, 
                "body > div.l-wrapper > div > header > h1"
            )
            if not job_info['title']:
                print_and_logging("タイトルの取得に失敗しました")

            # 終了チェック
            header_div = soup.select_one("body > div.l-wrapper > div > header > div")
            job_info["end"] = bool(header_div and "終了" in header_div.text)

            # セクション内の全てのdl要素を取得
            section = soup.select_one("body > div.l-wrapper > div > section")
            if section:
                dl_elements = section.find_all("dl")
                has_summary = False

                for dl in dl_elements:
                    try:
                        dt = dl.find("dt")
                        dd = dl.find("dd")
                        if dt and dd:
                            key = dt.text.strip()
                            value = dd.text.strip()
                            job_info[key] = value
                            
                            # 概要または詳細キーのチェック
                            if "概要" in key or "詳細" in key or "目的" in key or "背景" in key:
                                has_summary = True
                    except AttributeError:
                        continue

                # 概要・詳細の取得状態をフラグとして保存
                job_info["is_succeeded_get_info"] = has_summary

            return job_info
            
        except Exception as e:
            print_and_logging(f"jobs descriptionをスクレイピングする際にエラーが発生しました: {str(e)}")
            return None

    @classmethod
    def scrape_multiple_jobs(cls, urls):
        """
        複数のLancers案件の詳細情報を取得する
        
        Args:
            urls (list): Lancers案件のURLリスト
            
        Returns:
            list: 各案件の詳細情報を含む辞書のリスト
        """
        results = []
        for url in urls:
            job_details = cls.get_job_details(url)
            if job_details:
                results.append(job_details)
        return results
