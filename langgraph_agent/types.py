from typing import Annotated, List, Dict, Any, Optional, Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import datetime

from langgraph.graph import add_messages


class AgentState(TypedDict):
    """エージェントの状態を表す型定義"""
    #messages: Annotated[List[HumanMessage | AIMessage | ToolMessage], add_messages]
    route: str
    dismiss_reason: str
    jobs_description: str
    user_introduction: str
    user_name: str  # デフォルト値はコード内で設定
    selection_criteria: str
    suggestion_sentence: str
    url: str
