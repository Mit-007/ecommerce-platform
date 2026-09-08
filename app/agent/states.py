from typing import TypedDict


# =========
# Agent state Schema
# =========
class AgentState(TypedDict):
    question : str
    final_answer : str
    tool_calls : list
    tool_call_log : list[dict]
    previous_chat : list[dict]