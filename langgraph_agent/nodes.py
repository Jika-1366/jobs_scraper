from typing import Union
from .types import AgentState
import os
from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState

from langchain_core.messages import (HumanMessage, AIMessage, ToolMessage, 
                                     BaseMessage, SystemMessage, RemoveMessage)

from .types import AgentState
from .control_models import get_normal_llm
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

class Router(TypedDict):
    route: Literal["apply", "dismiss"]
    dismiss_reason: str
    
#raw_model = get_normal_llm("gemini-1.5-flash") #gemini-exp-1121
#raw_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, google_api_key=os.getenv('GEMINI_API_KEY'))
raw_model = get_normal_llm("gpt-4o-mini")
router_model = raw_model.with_structured_output(Router)

def router_node(state: AgentState):
    system_message = SystemMessage(content=f"""
                      選考基準(Selection Criteria)に基づいて、ユーザーがこの仕事に応募するべきかどうかを判断してください。\n
                      dismiss_reasonはdismissの場合のみ、記入していただきたい。applyの場合は空白でOK。\n
                      選考基準: {state["selection_criteria"]}\n
                      """)
    job_description_message = HumanMessage(content=f"仕事内容: {state['jobs_description']}")
    messages = [system_message, job_description_message]
    router_response = router_model.invoke(messages)
    print("router_response:", router_response)
    return {"route": router_response["route"], "dismiss_reason":router_response["dismiss_reason"]}

def route_after_selection(state: AgentState) -> Literal["write_suggestion_node", END]:
    if state["route"] == "apply":
        return "write_suggestion_node"
    else:
        return END

def write_suggestion_node(state: AgentState):
    system_message = SystemMessage(content=f"""
                    あなたはプロのキャリアライターであり、発注者（Orderer）に対して私のスキルと経験を最大限にアピールできる提案文を作成する専門家です。以下の情報をもとに、魅力的で誠実な提案文を作成してください。

                    提案文の目的
                    発注者が「この人に依頼したい！」と思うような自己PR文を作成してください。特に次の点を強調してください：

                    スキルの具体性と信頼性
                    実績や使用経験のある技術について具体的に記載し、信頼感を与える文章にしてください。

                    柔軟性とコストパフォーマンス
                    報酬に関係なく、柔軟に対応し、高品質な仕事を提供する姿勢を明確にしてください。
                    
                    ユーザー名: {state["user_name"]}\n
                    ユーザーの強みと情報: {state["user_introduction"]}\n
                    これらの情報に基づいて、ユーザーが仕事の応募をする際の提案文を作成してください。
                    納期や報酬も提案しましょう。人気になりそうな案件は応募する仕事内容(募集者の提案する報酬)よりも低い報酬と早い納期を提案しましょう。
                    出力形式を次のようにしてください：

                    タイトルや見出しには###などのマークダウン記法を使用せず、普通の文章として書いてください。
                    改行には\nなどのエスケープシーケンスを使用せず、普通に改行してください。
                    可能な限りシンプルで、読みやすい形式にしてください。
                    """)
    job_description_message = HumanMessage(content=f"応募する仕事内容: {state['jobs_description']}")
    messages = [system_message, job_description_message]
    suggestion_sentence = raw_model.invoke(messages).content
    return {"suggestion_sentence": suggestion_sentence}
    




# Example usage
if __name__ == "__main__":
    # Create a sample conversation
    sample_messages = [
        HumanMessage(content="Hello, AI!"),
        AIMessage(content="Hello! How can I assist you today?"),
        ToolMessage(content="Fetched current weather data.", tool_call_id="1"),
        HumanMessage(content="What's the weather like?"),
        AIMessage(content="Based on the data, the current weather is sunny with a temperature of 25°C."),
        HumanMessage(content="That's nice. Can you recommend some outdoor activities?"),
        AIMessage(content="Certainly! Given the pleasant weather, here are some outdoor activities you might enjoy:..."),
        ToolMessage(content="Retrieved list of popular outdoor activities in the area.", tool_call_id="2"),
    ]
