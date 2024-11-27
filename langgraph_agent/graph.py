
from langgraph.graph import StateGraph, END
from .types import AgentState
import traceback
from langgraph.graph import StateGraph, START, END, MessagesState
from typing import Annotated, Literal
from mem0 import Memory
import json
from langgraph.prebuilt import ToolNode

# langchain関連
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

from .control_models import get_model
from .nodes import router_node, route_after_selection,  write_suggestion_node


tools = []

tools_by_name = {tool.name: tool for tool in tools}
# Define our tool node
def tool_node(state: AgentState):
    is_suggest_new_reminders:bool = False
    outputs = []
    new_reminders_suggestions = []
    for tool_call in state["messages"][-1].tool_calls:
        try:
            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            print_and_logging(tool_call["args"].get("get_full_content_even_if_file_is_so_large",None))
            if tool_call["name"]=="get_file_content" and tool_call["args"].get("get_full_content_even_if_file_is_so_large",None):
                pass
            else:
                if len(str(tool_result)) >= 2000:
                    #tool_result = shorten_tool_result(tool_result)
                    pass
            tool_name = tool_call["name"]
            if tool_name=="suggest_new_reminders_periodic" or tool_name == "suggest_new_reminders_once" :
                new_reminders_suggestions+=tool_result #List[NewReminder]
                is_suggest_new_reminders=True
                tool_result = "新しいremindersを提案候補に入れました"
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result, ensure_ascii=False),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        except Exception as e:
            error_message = f"tool_nodeで、エラーが発生しました: {str(e)}"
            if len(error_message) >= 1000:
                error_message = f"前半: {error_message[:500]} ... 後半: {error_message[-500:]}"
            outputs.append(
                ToolMessage(
                    content=error_message,
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
    if is_suggest_new_reminders:
        return {"messages":outputs, "new_reminders_suggestions":new_reminders_suggestions}
    else:
        return {"messages": outputs}

async def create_graph() -> StateGraph:
    """グラフの構築"""
    # StateGraphの定義
    workflow = StateGraph(AgentState)

    # ノードの追加
    workflow.add_node("router_node", router_node)
    workflow.add_node("write_suggestion_node", write_suggestion_node)
    
    # エッジの追加
    workflow.add_edge(START, "router_node")
    workflow.add_conditional_edges(
        "router_node",
        route_after_selection,
        {
            "write_suggestion_node": "write_suggestion_node",
            END: END
        }
    )
    workflow.add_edge("write_suggestion_node",END)
    
    
    # グラフのコンパイル
    return workflow.compile()
