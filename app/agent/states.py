from typing import TypedDict ,Any
from uuid import UUID

# =========
# Agent state Schema
# =========
class AgentState(TypedDict):
    """
    Agent state schema.
    """
    question : str
    final_answer : Any
    tool_calls : list
    tool_call_log : list[dict]
    previous_chat : list[dict]
    conversation_id : UUID