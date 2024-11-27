import os
import datetime
import traceback
from langchain_core.messages import HumanMessage
from .graph import create_graph
from .types import AgentState
from .category_classifier import classify_job_category
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

# Get from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")

def read_text_file(file_path: str) -> str:
    """テキストファイルを読み込む関数"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, file_path)
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print_and_logging(f"ファイル読み込みエラー {file_path}: {e}")
        return ""

# グラフの作成（非同期）
app = None

async def initialize_graph():
    global app
    if app is None:
        app = await create_graph()
    return app

async def run_langgraph_agent_executor(jobs_description) -> str:
    """
    LangGraphを使用したエージェントエグゼキューターを実行する関数
    agent.pyのrun_agent_executorを置き換えることを想定しています。

    Args:
        jobs_description (str): 案件の説明文

    Returns:
        str: エージェントからの応答テキスト
    """
    # グラフの初期化を確認
    graph = await initialize_graph()

    async def run_conversation(jobs_description: str) -> dict: 
        # 仕事内容を分類
        category_result = classify_job_category(jobs_description)
        category = category_result["category"]
        
        # カテゴリに応じて適切なプロンプトを読み込む
        selection_criteria = read_text_file(f'prompt/selection_criteria_{category}.txt')
        user_introduction = read_text_file(f'prompt/user_introduction_{category}.txt')

        print_and_logging(f"選択基準ファイル: selection_criteria_{category}.txt")
        print_and_logging(f"自己紹介ファイル: user_introduction_{category}.txt")
        
        agentstate = {
            "jobs_description": jobs_description, 
            "user_introduction": user_introduction,
            "user_name": "kota",  
            "selection_criteria": selection_criteria,
            "suggestion_sentence": "",
            "url": ""
        }
        
        response_suggestion_sentence = ""
        response_dismiss_reason = ""
        async for event in graph.astream(agentstate):
            for value in event.values():
                if not isinstance(value, dict):
                    continue
                if value.get("suggestion_sentence"):
                    # 配列全体を文字列として結合
                    streamed_suggestion_sentence = "".join(value["suggestion_sentence"])
                    response_suggestion_sentence = streamed_suggestion_sentence
                if value.get("dismiss_reason"):
                    # 配列全体を文字列として結合
                    streamed_dismiss_reason = "".join(value["dismiss_reason"])
                    response_dismiss_reason = streamed_dismiss_reason
                
        # 蓄積したメッセージを結合して返す
        return {"suggestion": response_suggestion_sentence, "dismiss_reason": response_dismiss_reason}
    
    try:
        response = await run_conversation(jobs_description)
        suggestion_sentence = response.get("suggestion", "")
        dismiss_reason = response.get("dismiss_reason", "")
    except Exception as e:
        # エラー情報を詳細に取得
        error_details = traceback.format_exc()
        print_and_logging(f"run_conversation 関数でエラーが発生しました: {e}")
        print_and_logging("トレースバックの詳細:", error_details)   
        suggestion_sentence = ""
        dismiss_reason = f"run_conversation 関数でエラーが発生しました: {e}"
    
    if not suggestion_sentence and not dismiss_reason:
        print_and_logging("提案と却下理由の両方が空です。")
        
    return suggestion_sentence, dismiss_reason
