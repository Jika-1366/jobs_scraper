from google.gmail_handler import get_lancers_urls
from scraping.scraping import get_job_details
from langgraph_agent.agent_executor import run_langgraph_agent_executor
import asyncio
import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

def process_job_details(job):
    """案件情報を処理して表示し、文字列として返す"""
    print_and_logging("\n=== 案件情報 ===")
    for key, value in job.items():
        print_and_logging(f"{key}: \n{value}\n")
    print_and_logging("===============")

    # 案件情報を1つの文字列に結合（フォーマットを修正）
    jobs_description = []
    for key, value in job.items():
        jobs_description.append(f"{key}: {value}")
    
    return "\n".join(jobs_description)

async def get_ai_suggestion(jobs_description):
    """AIからの提案を取得して表示する"""
    suggestion, dismiss_reason = await run_langgraph_agent_executor(jobs_description)
    print_and_logging("\n=== AIからの提案 ===")
    print_and_logging(f"提案: {suggestion}")
    if dismiss_reason:
        print_and_logging(f"却下理由: {dismiss_reason}")
    print_and_logging("===============")
    return suggestion, dismiss_reason

def display_results(good_jobs, rejected_jobs):
    """結果を表示する"""
    print_and_logging("\n=== 応募可能な案件 ===")
    for url, (suggestion, _) in good_jobs.items():
        print_and_logging(f"URL: {url}")
        print_and_logging(f"提案: {suggestion}\n")

    print_and_logging("\n=== 不採用の案件 ===")
    for url, (_, dismiss_reason) in rejected_jobs.items():
        print_and_logging(f"URL: {url}")
        print_and_logging(f"不採用理由: {dismiss_reason}\n")

def load_existing_jobs(filename):
    """既存のジョブデータをJSONファイルからロードする"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_jobs_to_json(good_jobs, rejected_jobs):
    """ジョブデータをJSONファイルに保存する"""
    os.makedirs('data', exist_ok=True)
    
    # 既存のデータをロード
    existing_good_jobs = load_existing_jobs('data/good_jobs.json')
    existing_rejected_jobs = load_existing_jobs('data/rejected_jobs.json')
    
    # 新しいデータを追加
    existing_good_jobs.update(good_jobs)
    existing_rejected_jobs.update(rejected_jobs)
    
    # JSONファイルに保存 (indent=4を使用)
    with open('data/good_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(existing_good_jobs, f, ensure_ascii=False, indent=4)
    
    with open('data/rejected_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(existing_rejected_jobs, f, ensure_ascii=False, indent=4)

async def process_job_batch(urls):
    """特定のURLバッチを処理する関数"""
    good_jobs = {}
    rejected_jobs = {}

    # 取得したURLから案件情報をスクレイピング
    for url in urls:
        job = get_job_details(url)
        if job:
            # 案件情報を処理
            jobs_description = process_job_details(job)
            
            # AIからの提案を取得
            suggestion, dismiss_reason = await get_ai_suggestion(jobs_description)

            # suggestionの有無に基づいて案件を分類
            if suggestion:
                good_jobs[url] = (suggestion, dismiss_reason)
            else:
                rejected_jobs[url] = (suggestion, dismiss_reason)

    # 結果の表示
    display_results(good_jobs, rejected_jobs)
    
    # JSONファイルに保存
    save_jobs_to_json(good_jobs, rejected_jobs)

    return good_jobs, rejected_jobs

async def process_lancers_jobs():
    """Lancersの案件を繰り返し処理する関数"""
    while True:
        # Gmailから未読のLancersメールを取得し、URLを抽出
        urls = get_lancers_urls()
        if not urls:
            print_and_logging("新しい案件はありません。")
            break

        await process_job_batch(urls)

async def test_process_lancers_jobs(max_iterations=2):
    """テスト用の関数: 指定された回数だけ処理を実行する"""
    iterations = 0
    while iterations < max_iterations:
        # Gmailから未読のLancersメールを取得し、URLを抽出
        urls = get_lancers_urls()
        if not urls:
            print_and_logging("新しい案件はありません。")
            break

        await process_job_batch(urls)
        iterations += 1

    return iterations

if __name__ == "__main__":
    # すべての未読メールを処理するように変更
    asyncio.run(process_lancers_jobs())
