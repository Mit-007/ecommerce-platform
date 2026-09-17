from typing import Literal
from app.agent.states import AgentState
from app.core.logger import logger
from app.services.llm_service import get_llm
from app.services.prompt_template import get_chat_agent_prompt
from app.client.client import get_mcp_tools_dict
from app.core.constant import MAXIMUM_TOOL_CALLS

# =========================
# call_llm
# =========================
async def call_llm(state: AgentState) -> AgentState:
    """
    Call LLM for generating answer. LLM sees tool results
    from previous executions to avoid repeating same calls.
    """
    logger.info("Node: call_llm")
    try:
        question = state.get("question", "")

        if not question or not question.strip():
            raise ValueError("Invalid input: question is empty.")

        previous_chat = state.get("previous_chat", [])
        tool_call_log = state.get("tool_call_log", [])

        # Create prompt with full context
        llm_prompt = get_chat_agent_prompt(
            question=question,
            previous_chat=previous_chat,
            tool_call_log=tool_call_log,
        )

        # Get LLM
        llm = get_llm()

        if llm is None:
            raise RuntimeError("LLM service is not available.")

        logger.info(f"LLM call #{len(tool_call_log) + 1}")
        result = await llm.ainvoke(llm_prompt)
        logger.info("LLM response received")

        if result is None:
            raise RuntimeError("LLM returned an empty response.")

        tool_calls = getattr(result, "tool_calls", [])

        logger.info(f"Tool calls requested: {len(tool_calls)}")

        return {
            "final_answer": result,
            "tool_calls": tool_calls,
        }

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise RuntimeError(f"Failed to execute LLM node: {e}") from e


# =========================
# route_tool_node
# =========================
def route_tool_node(state: AgentState) -> Literal["tool_node", "END"]:
    """
    Route to tool_node if tools are requested and limit not exceeded.
    """
    logger.info("Node: route_tool_node")
    try:
        tool_calls = state.get("tool_calls", [])
        tool_call_log = state.get("tool_call_log", [])
        total_calls = len(tool_call_log) + len(tool_calls)

        if not tool_calls:
            logger.info("No tool calls - routing to END")
            return "END"

        if total_calls > MAXIMUM_TOOL_CALLS:
            logger.warning(
                f"Maximum tool calls exceeded: {total_calls} > {MAXIMUM_TOOL_CALLS}. "
                f"Routing to END to prevent infinite loop."
            )
            return "END"

        logger.info(f"Routing to tool_node ({len(tool_calls)} new calls)")
        return "tool_node"

    except Exception as e:
        logger.error(f"Routing failed: {e}")
        raise RuntimeError(f"Failed to route tool node: {e}") from e


# =========================
# tool_node
# =========================
async def tool_node(state: AgentState) -> AgentState:
    """
    Execute MCP tools and return results to be added to chat history.
    """
    logger.info("Node: tool_node")
    try:
        tools_dict = get_mcp_tools_dict()

        if not tools_dict:
            raise RuntimeError("MCP tools are not available.")

        tool_calls = state.get("tool_calls", [])

        if not tool_calls:
            return {"tool_call_log": state.get("tool_call_log", [])}

        tool_call_log = state.get("tool_call_log", [])

        # Execute each tool
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})

            if not tool_name:
                raise ValueError("Tool name is missing in tool call.")

            logger.info(f"Executing tool: {tool_name}")

            # Find tool
            tool = tools_dict.get(tool_name)

            if tool is None:
                raise ValueError(f"Tool '{tool_name}' not found.")

            # Add conversation_id for specific tools
            if tool_name == "create_support_ticket":
                conversation_id = state.get("conversation_id")
                if not conversation_id:
                    raise ValueError("conversation_id is required for create_support_ticket.")
                if "request" not in tool_args:
                    raise ValueError("Request data is missing for create_support_ticket.")
                tool_args["request"]["conversation_id"] = conversation_id

            # Execute tool
            try:
                result = await tool.ainvoke(tool_args)
            except Exception as e:
                logger.error(f"Tool execution failed for '{tool_name}': {e}")
                result = {"success": False, "error": f"Tool execution failed: {str(e)}"}

            # Log execution
            tool_call_log.append({
                "tool_name": tool_name,
                "tool_args": tool_args,
                "tool_answer": result,
            })

            logger.info(f"Tool '{tool_name}' completed successfully")

        return {"tool_call_log": tool_call_log}

    except RuntimeError:
        raise

    except Exception as e:
        logger.error(f"Tool node execution failed: {e}")
        raise RuntimeError(f"Failed to execute tool node: {e}") from e