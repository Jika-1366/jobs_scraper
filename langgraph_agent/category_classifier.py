from typing import Literal, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from .control_models import get_normal_llm

class CategoryClassification(TypedDict):
    category: Literal["dev", "task", "english"]

raw_model = get_normal_llm("gpt-4o-mini")
classifier_model = raw_model.with_structured_output(CategoryClassification)

def classify_job_category(job_description: str) -> CategoryClassification:
    """
    仕事の内容を分析し、適切なカテゴリ（dev/task/english）に分類する
    """
    system_prompt = """
    仕事の内容を分析し、以下の3つのカテゴリのいずれかに分類してください：

    1) 開発系・LLM系 (dev)
    - 生成AI活用・業務効率化
    - 業務システム・ツール開発
    - AI（人工知能）・機械学習・ChatGPT

    2) 作業系 (task)
    - メール・フォーム送信代行
    - 営業・テレアポ代行の副業
    - 資料作成サポート副業
    - お問い合わせ対応・カスタマーサポート
    - データ収集・入力・リスト作成
    - テキスト入力・タイピング・キーパンチ
    - データ閲覧・検索・登録
    - テープ起こし・文字起こし・書き起こし
    - データ整理・分類・カテゴリ分け

    3) 英語系 (english)
    - 英語翻訳・英文翻訳
    - 映像翻訳・出版翻訳・メディア翻訳

    仕事の内容を慎重に分析し、最も適切なカテゴリを選択してください。
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"仕事内容: {job_description}")
    ]

    return classifier_model.invoke(messages)
