from utils.logging_utils import print_and_logging

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

def display_results(good_jobs, rejected_jobs, ignored_jobs):
    """結果を表示する"""
    print_and_logging("\n=== 応募可能な案件 ===")
    for url, (suggestion, _) in good_jobs.items():
        print_and_logging(f"URL: {url}")
        print_and_logging(f"提案: {suggestion[:20]}...\n")

    print_and_logging("\n=== 不採用の案件 ===")
    for url, (_, dismiss_reason) in rejected_jobs.items():
        print_and_logging(f"URL: {url}")
        print_and_logging(f"不採用理由: {dismiss_reason}\n")

    print_and_logging("\n=== NGワードにより無視された案件 ===")
    for url in ignored_jobs:
        print_and_logging(f"URL: {url}")
