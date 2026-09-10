from typing import Literal
from app.agent.states import AgentState
from app.core.logger import logger
from app.services.llm_service import get_llm
from app.services.prompt_templete import get_chat_agent_prompt
from app.client.client import get_mcp_tools_dict


# =========================
# call_llm
# =========================
async def call_llm(state: AgentState) -> AgentState:
    logger.info("Node:-call_llm")

    try:
        question = state.get("question", "")

        if not question or not question.strip():
            raise ValueError("Invalid input: question is empty.")

        previous_chat = state.get("previous_chat",[],)

        tool_call_log = state.get("tool_call_log",[],)

        # Create prompt
        llm_prompt = get_chat_agent_prompt(
            question=question,
            previous_chat=previous_chat,
            tool_call_log=tool_call_log,
        )

        # Get LLM
        llm = get_llm()

        if llm is None:
            raise RuntimeError("LLM service is not available.")

        # -------------------------
        # Call LLM
        # -------------------------
        result = await llm.ainvoke(llm_prompt)

        if result is None:
            raise RuntimeError("LLM returned an empty response.")

        tool_calls = getattr(result,"tool_calls",[],)

        logger.info(
            f"LLM response received. "
            f"tool_calls={len(tool_calls)}"
        )

        return {
            "final_answer": result,
            "tool_calls": tool_calls,
        }

    except ValueError as e:
        logger.exception(f"Validation error in call_llm: {e}")
        raise

    except Exception as e:
        logger.exception(f"Unexpected error in call_llm: {e}")
        raise RuntimeError(f"Failed to execute LLM node: {e}") from e


# =========================
# route_tool_node
# =========================
def route_tool_node(
    state: AgentState,
) -> Literal["tool_node", "END"]:
    """
    Route to the tool node if the LLM
    requested one or more tools.
    """
    logger.info("Node:-route_tool_node")
    try:
        tool_calls = state.get("tool_calls",[],)

        if tool_calls:
            logger.info(
                f"Routing to tool_node. "
                f"Tool calls={len(tool_calls)}"
            )
            return "tool_node"

        logger.info("No tool calls found.Routing to END.")

        return "END"

    except Exception as e:
        logger.exception(f"Error in route_tool_node: {e}")
        raise RuntimeError(f"Failed to route tool node: {e}") from e


# =========================
# tool_node
# =========================
async def tool_node(
    state: AgentState,
) -> AgentState:
    """
    Execute MCP tools asynchronously.
    """
    logger.info("Node:-tool_node")
    try:
        # Get MCP tools
        tools_dict = get_mcp_tools_dict()

        if not tools_dict:
            raise RuntimeError("MCP tools are not available.")

        # Get tool calls
        tool_calls = state.get("tool_calls",[],)

        if not tool_calls:
            logger.info("No tool calls to execute.")

            return {
                "tool_call_log": state.get("tool_call_log",[]),
            }

        # Get existing tool log
        tool_call_log = state.get("tool_call_log",[],)

        # --------------
        # Execute tools
        # -------------
        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name")

                tool_args = tool_call.get("args",{})

                if not tool_name:
                    raise ValueError("Tool name is missing.")

                logger.info(
                    f"Executing tool: {tool_name} "
                    f"with args: {tool_args}"
                )

                # Find tool
                tool = tools_dict.get(tool_name)

                if tool is None:
                    raise ValueError(f"Tool '{tool_name}' not found in mcp tool dict.")

                # Add conversation ID
                if (tool_name== "create_support_ticket"):
                    conversation_id = state.get("conversation_id")

                    if conversation_id is None:
                        raise ValueError("conversation_id is required for create_support_ticket.")

                    if "request" not in tool_args:
                        raise ValueError("Request data is missing for create_support_ticket.")

                    tool_args["request"]["conversation_id"] = conversation_id

                # -------------------------
                # Execute MCP tool
                # -------------------------
                result = await tool.ainvoke(tool_args)

                if result is None:
                    logger.warning(
                        f"Tool '{tool_name}' returned empty result")

                # Store tool execution log
                tool_dict = {
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                    "tool_answer": result,
                }

                tool_call_log.append(tool_dict)

                logger.info(f"Tool '{tool_name}' executed successfully: ")

            except Exception as e:
                logger.exception(
                    f"Error executing tool '{tool_call.get('name', 'unknown')}': {e}")

                raise RuntimeError(f"Failed to execute tool '{tool_call.get('name', 'unknown')}': {e}") from e

        return {
            "tool_call_log": tool_call_log,
        }

    except RuntimeError:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error in tool_node: {e}")
        
        raise RuntimeError(f"Failed to execute tool node: {e}") from e