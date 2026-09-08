from fastapi import APIRouter
from pydantic import BaseModel
from app.database.repositories.converstion_repositories import get_conversation_by_id , append_conversation_messages, create_new_conversation
from app.agent.graph import agent
from app.core.logger import logger
from uuid import UUID

router = APIRouter(
    prefix="",
    tags=["Chat Bot Routes"]
)


class AgentRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    customer_id : UUID | None = None


@router.post("/agent_call")
async def call_ai_agent(request: AgentRequest):
    try:
        # Get data from frontend
        user_question = request.message
        conversation_id = request.conversation_id

        past_converstion = None

        if conversation_id== None:
            past_converstion = create_new_conversation(request.customer_id,title=user_question.strip()[:25].rstrip())
            conversation_id = past_converstion[0]

        else :
            past_converstion = get_conversation_by_id(conversation_id)

        input_state = {
            "question": user_question,
            "tool_call_log": [],
            "previous_chat": past_converstion,
        }

        config = {
            "configurable": {
                "thread_id": conversation_id or "thread-1"
            }
        }

        # Async LangGraph execution
        response = await agent.ainvoke(
            input_state,
            config=config,
        )

        new_messages_list = [
            {
                "role" : "user",
                "content" : user_question
            },
            {
                "role" : "AI",
                "content" : response['final_answer'].content[0]['text']
            }
        ]

        append_conversation_messages(conversation_id,new_messages_list)

        return {
            "message": response,
            "chat" : past_converstion,
            "new" : new_messages_list
        }

    except Exception as e:
        logger.exception(f"Agent error: {e}")

        return {
            "message": "Error !!",
        }