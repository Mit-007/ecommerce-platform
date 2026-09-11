from fastapi import APIRouter, HTTPException
from app.database.repositories.conversation_repositories import (
    get_conversation_by_id,
    append_conversation_messages,
    create_new_conversation,
)
from app.agent.graph import agent
from app.core.logger import logger
from app.model.support_agent_schema import AgentRequest
from app.services.extract_response import extract_response_text

router = APIRouter(prefix="/agent",tags=["Chat Bot Routes"])

@router.post("/call")
async def call_ai_agent(request: AgentRequest):
    """
    invoke agent and return llm response.
    """
    try:
        user_question = request.message.strip()
        conversation_id = request.conversation_id

        if not user_question:
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty.",
            )

        past_conversation = []

        if not conversation_id:
            new_conversation = create_new_conversation(
                request.customer_id,
                title=user_question[:25].rstrip(),
            )

            if not new_conversation:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create conversation.",
                )

            conversation_id = new_conversation[0]

        else:
            conversation = get_conversation_by_id(conversation_id)

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Conversation with ID {conversation_id} not found.",
                )

            past_conversation = conversation[3] or []

        input_state = {
            "question": user_question,
            "tool_call_log": [],
            "previous_chat": past_conversation,
            "conversation_id": conversation_id,
        }

        response = await agent.ainvoke(input_state)

        final_answer = extract_response_text(response["final_answer"])

        new_messages_list = [
            {
                "role": "user",
                "content": user_question,
            },
            {
                "role": "assistant",
                "content": final_answer,
            },
        ]

        append_conversation_messages(
            conversation_id,
            new_messages_list,
        )

        return {
            "conversation_id": str(conversation_id),
            "message": final_answer,
            "chat": past_conversation,
            "new": new_messages_list,
        }

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process AI agent request.",
        )