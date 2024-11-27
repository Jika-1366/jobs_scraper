import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agent.agent_executor import run_langgraph_agent_executor

async def test_agent_executor():
    jobs_description = "このお仕事は時給300円で雑草を引き抜く仕事です。朝７時に新宿のとあるビルで仕事開始です。"
    suggestion, dismiss_reason = await run_langgraph_agent_executor(jobs_description)
    print("提案文:", suggestion)
    print("却下理由:", dismiss_reason)

if __name__ == "__main__":
    asyncio.run(test_agent_executor())
