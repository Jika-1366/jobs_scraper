import os
import yaml
from utils.logging_utils import print_and_logging

def load_ignore_words():
    """jobignore.yamlからNGワードリストを読み込む"""
    ignore_file = 'data/jobignore.yaml'
    if os.path.exists(ignore_file):
        with open(ignore_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('ignore_words', [])
    return []

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
