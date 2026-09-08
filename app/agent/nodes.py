from typing import Literal
from app.agent.states import AgentState
from app.core.logger import logger
from app.services.llm_service import get_llm
from app.services.chat_agent_prompt import get_chat_agent_prompt
from app.client.client import get_mcp_tools_dict


# =========================
# call_llm
# =========================
async def call_llm(state: AgentState) -> AgentState:
    logger.info("Node:-call_llm")

    try:
        if state["question"].strip() == "":
            raise ValueError("Invalid Input, question is empty")

        llm_prompt = get_chat_agent_prompt(
            state["previous_chat"],
            state["question"],
            state["tool_call_log"],
        )

        llm = get_llm()

        if not llm:
            raise ValueError("LLM service is not available.")

        # Async LLM call
        result = await llm.ainvoke(llm_prompt)

        tool_calls = result.tool_calls

        return {
            "final_answer": result,
            "tool_calls": tool_calls,
        }

    except Exception as e:
        logger.exception(f"Error in call_llm: {e}")
        raise


# =========================
# route_tool_node
# =========================
def route_tool_node(
    state: AgentState,
) -> Literal["tool_node", "END"]:
    """Route to the tool node if a tool is required."""

    logger.info("Node:-route_tool_node")

    try:
        if state["tool_calls"]:
            return "tool_node"

        return "END"

    except Exception as e:
        logger.exception(f"Error in route_tool_node: {e}")
        raise


# =========================
# tool_node
# =========================
async def tool_node(state: AgentState) -> AgentState:
    """Execute MCP tools asynchronously."""

    logger.info("Node:-tool_node")

    try:
        tools_dict = get_mcp_tools_dict()

        for tool_call in state["tool_calls"]:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            logger.info(
                f"Executing tool: {tool_name} "
                f"with args: {tool_args}"
            )

            tool = tools_dict.get(tool_name)

            if not tool:
                raise ValueError(
                    f"Tool '{tool_name}' not found."
                )

            # Async MCP tool execution
            result = await tool.ainvoke(tool_args)

            tool_dict = {
            "tool_name":tool_name,
            "tool_args":tool_args,
            "tool_answer":result
            }

            state['tool_call_log'].append(tool_dict)

        return {
            "tool_call_log": state['tool_call_log'],
        }

    except Exception as e:
        logger.exception(f"Error in tool_node: {e}")
        raise