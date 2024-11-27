from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging

def get_model(model_name, tools = []):
    if len(tools) == 0:
        print_and_logging("toolsの数がゼロ個です。")
    if "gpt" in model_name or "o1" in model_name:
        #gpt-4o-2024-08-06
        return ChatOpenAI(model=model_name, temperature=0.9, api_key=os.getenv('OPENAI_API_KEY')).bind_tools(tools)
    elif "claude" in model_name:
        return ChatAnthropic(model=model_name, temperature=0.9, api_key=os.getenv('ANTHROPIC_API_KEY')).bind_tools(tools)
    elif "gemini" in model_name:
        return ChatGoogleGenerativeAI(model=model_name, temperature=0.9, google_api_key=os.getenv('GEMINI_API_KEY')).bind_tools(tools)
    else:
        raise ValueError(f"Unsupported LLM model: {model_name}")

def get_normal_llm(llm_model):
    
    if "gpt" in llm_model:
        llm = ChatOpenAI(model=llm_model, temperature=0.9, api_key=os.getenv('OPENAI_API_KEY'))
    elif "claude" in llm_model:
        llm = ChatAnthropic(model=llm_model, temperature=0.9, api_key=os.getenv('ANTHROPIC_API_KEY'))
    elif "gemini" in llm_model:
        llm = ChatGoogleGenerativeAI(model=llm_model, temperature=0.9, google_api_key=os.getenv('GEMINI_API_KEY'))
    else:
        raise ValueError(f"Unsupported LLM model: {llm_model}")

    return llm