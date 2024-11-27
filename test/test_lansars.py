import requests
from bs4 import BeautifulSoup
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging
# 対象のURL（仮置き）
url = "https://www.lancers.jp/work/detail/5155653?ref=jobsearch_clip_mail"  # 実際のURLに置き換える

# ヘッダーを設定（場合によっては必要）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# HTMLを取得
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "lxml")

    # 必要な情報を抽出
    # タイトル
    title = soup.select_one("body > div.l-wrapper > div > header > h1").text.strip()

    # 依頼主の業種
    industry = soup.select_one("body > div.l-wrapper > div > section > dl:nth-child(9) > dd").text.strip()
    # 提示した予算
    budget = soup.select_one("body > div.l-wrapper > div > section > dl:nth-child(10) > dd").text.strip()
    # 依頼概要
    summary = soup.select_one("body > div.l-wrapper > div > section > dl:nth-child(11) > dd").text.strip()

    # 結果を表示
    print_and_logging(f"タイトル: {title}")
    print_and_logging(f"依頼主の業種: {industry}")
    print_and_logging(f"提示した予算: {budget}")
    print_and_logging(f"依頼概要: {summary}")
else:
    print_and_logging(f"ページを取得できませんでした (HTTP {response.status_code})")
