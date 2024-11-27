from google.gmail_handler import get_lancers_urls
from scraping.scraping import get_job_details

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

def main():
    # Gmailから未読のLancersメールを取得し、URLを抽出
    urls = get_lancers_urls()
    if not urls:
        print_and_logging("新しい案件はありません。")
        return

    # 取得したURLから案件情報をスクレイピング
    for url in urls:
        job = get_job_details(url)
        if job:
            print_and_logging("\n=== 案件情報 ===")
            for key, value in job.items():
                print_and_logging(f"{key}: \n{value}\n")
            print_and_logging("===============")

if __name__ == "__main__":
    main()
