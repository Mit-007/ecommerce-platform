from typing import TypedDict
from uuid import UUID

# =========
# Agent state Schema
# =========
class AgentState(TypedDict):
    question : str
    final_answer : any
    tool_calls : list
    tool_call_log : list[dict]
    previous_chat : list[dict]
    conversation_id : UUID