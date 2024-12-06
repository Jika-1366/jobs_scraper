import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_processing import process_lancers_jobs

if __name__ == "__main__":
    # すべての未読メールを処理
    asyncio.run(process_lancers_jobs())
