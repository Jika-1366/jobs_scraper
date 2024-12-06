from google.gmail_handler import get_lancers_urls
from google.email_sender import send_email
from scraping.scraping import get_job_details
from langgraph_agent.agent_executor import run_langgraph_agent_executor
from utils.logging_utils import print_and_logging
from .data_handler import load_ignore_words, save_jobs_to_yaml
from .job_filter import process_job_details, display_results

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

async def get_ai_suggestion(jobs_description):
    """AIからの提案を取得して表示する"""
    suggestion, dismiss_reason = await run_langgraph_agent_executor(jobs_description)
    print_and_logging("\n=== AIからの提案 ===")
    print_and_logging(f"提案: {suggestion}")
    if dismiss_reason:
        print_and_logging(f"却下理由: {dismiss_reason}")
    print_and_logging("===============")
    return suggestion, dismiss_reason

async def process_lancers_jobs():
    """Lancersの案件を繰り返し処理する関数"""
    # NGワードを一度だけ読み込む
    ignore_words = load_ignore_words()
    
    # 全ての良い案件を保存するリスト
    all_good_jobs = {}
    
    while True:
        # Gmailから未読のLancersメールを取得し、URLを抽出
        urls = get_lancers_urls()
        if not urls:
            print_and_logging("新しい案件はありません。")
            break

        good_jobs, _ = await process_job_batch(urls, ignore_words)
        all_good_jobs.update(good_jobs)

    # 良い案件がある場合のみメール送信
    if all_good_jobs:
        # メール本文の作成
        email_body = "以下の案件が見つかりました：\n\n"
        for url, (suggestion, _) in all_good_jobs.items():
            email_body += f"案件URL: {url}\n"
            email_body += f"AIからの提案:\n{suggestion}\n\n"
            email_body += "-------------------\n\n"
        
        # メール送信
        send_email(
            to="kotaro.kajitsuka@gmail.com",
            subject="新しい案件が見つかりました",
            body=email_body
        )

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
