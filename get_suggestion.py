from google.gmail_handler import get_lancers_urls
from scraping.scraping import get_job_details
from langgraph_agent.agent_executor import run_langgraph_agent_executor
import asyncio
import os
import sys
import yaml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

def load_ignore_words():
    """jobignore.yamlからNGワードリストを読み込む"""
    ignore_file = 'data/jobignore.yaml'
    if os.path.exists(ignore_file):
        with open(ignore_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('ignore_words', [])
    return []

def check_ignore_words(title: str, ignore_words: list) -> bool:
    """
    タイトルにNGワードが含まれているかチェックする
    
    Args:
        title: チェックする案件のタイトル
        ignore_words: NGワードのリスト
    
    Returns:
        bool: NGワードが含まれている場合はTrue
    """
    return any(word.lower() in title.lower() for word in ignore_words)

def process_job_details(job, ignore_words: list):
    """
    案件情報を処理して表示し、文字列として返す
    また、NGワードが含まれているかどうかをチェックする
    
    Args:
        job: 案件情報の辞書
        ignore_words: NGワードのリスト
    
    Returns:
        tuple: (jobs_description, should_ignore)
        - jobs_description: 案件情報の文字列
        - should_ignore: NGワードが含まれている場合はTrue
    """
    print_and_logging("\n=== 案件情報 ===")
    for key, value in job.items():
        print_and_logging(f"{key}: \n{value}\n")
    print_and_logging("===============")

    # NGワードチェック
    title = job.get('title', '')
    should_ignore = check_ignore_words(title, ignore_words)
    
    if should_ignore:
        print_and_logging("※ NGワードが含まれているため、この案件は無視されます")

    # 案件情報を1つの文字列に結合
    jobs_description = []
    for key, value in job.items():
        jobs_description.append(f"{key}: {value}")
    
    return "\n".join(jobs_description), should_ignore

async def get_ai_suggestion(jobs_description):
    """AIからの提案を取得して表示する"""
    suggestion, dismiss_reason = await run_langgraph_agent_executor(jobs_description)
    print_and_logging("\n=== AIからの提案 ===")
    print_and_logging(f"提案: {suggestion}")
    if dismiss_reason:
        print_and_logging(f"却下理由: {dismiss_reason}")
    print_and_logging("===============")
    return suggestion, dismiss_reason

def display_results(good_jobs, rejected_jobs, ignored_jobs):
    """結果を表示する"""
    print_and_logging("\n=== 応募可能な案件 ===")
    for url, (suggestion, _) in good_jobs.items():
        print_and_logging(f"URL: {url}")
        print_and_logging(f"提案: {suggestion}\n")

    print_and_logging("\n=== 不採用の案件 ===")
    for url, (_, dismiss_reason) in rejected_jobs.items():
        print_and_logging(f"URL: {url}")
        print_and_logging(f"不採用理由: {dismiss_reason}\n")

    print_and_logging("\n=== NGワードにより無視された案件 ===")
    for url in ignored_jobs:
        print_and_logging(f"URL: {url}")

def load_existing_jobs(filename):
    """既存のジョブデータをYAMLファイルからロードする"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def save_jobs_to_yaml(good_jobs, rejected_jobs):
    """ジョブデータをYAMLファイルに保存する"""
    os.makedirs('data', exist_ok=True)
    
    # 既存のデータをロード
    existing_good_jobs = load_existing_jobs('data/good_jobs.yaml')
    existing_rejected_jobs = load_existing_jobs('data/rejected_jobs.yaml')
    
    # 新しいデータを追加
    existing_good_jobs.update(good_jobs)
    existing_rejected_jobs.update(rejected_jobs)
    
    # YAMLファイルに保存
    with open('data/good_jobs.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(existing_good_jobs, f, allow_unicode=True)
    
    with open('data/rejected_jobs.yaml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(existing_rejected_jobs, f, allow_unicode=True)

async def process_job_batch(urls, ignore_words: list):
    """特定のURLバッチを処理する関数"""
    good_jobs = {}
    rejected_jobs = {}
    ignored_jobs = []

    # 取得したURLから案件情報をスクレイピング
    for url in urls:
        job = get_job_details(url)
        if job:
            # 案件情報を処理
            jobs_description, should_ignore = process_job_details(job, ignore_words)
            
            if should_ignore:
                ignored_jobs.append(url)
                continue

            # AIからの提案を取得
            suggestion, dismiss_reason = await get_ai_suggestion(jobs_description)

            # suggestionの有無に基づいて案件を分類
            if suggestion:
                good_jobs[url] = (suggestion, dismiss_reason)
            else:
                rejected_jobs[url] = (suggestion, dismiss_reason)

    # 結果の表示
    display_results(good_jobs, rejected_jobs, ignored_jobs)
    
    # YAMLファイルに保存
    save_jobs_to_yaml(good_jobs, rejected_jobs)

    return good_jobs, rejected_jobs

async def process_lancers_jobs():
    """Lancersの案件を繰り返し処理する関数"""
    # NGワードを一度だけ読み込む
    ignore_words = load_ignore_words()
    
    while True:
        # Gmailから未読のLancersメールを取得し、URLを抽出
        urls = get_lancers_urls()
        if not urls:
            print_and_logging("新しい案件はありません。")
            break

        await process_job_batch(urls, ignore_words)

async def test_process_lancers_jobs(max_iterations=2):
    """テスト用の関数: 指定された回数だけ処理を実行する"""
    # NGワードを一度だけ読み込む
    ignore_words = load_ignore_words()
    
    iterations = 0
    while iterations < max_iterations:
        # Gmailから未読のLancersメールを取得し、URLを抽出
        urls = get_lancers_urls()
        if not urls:
            print_and_logging("新しい案件はありません。")
            break

        await process_job_batch(urls, ignore_words)
        iterations += 1

    return iterations

if __name__ == "__main__":
    # すべての未読メールを処理するように変更
    asyncio.run(process_lancers_jobs())
