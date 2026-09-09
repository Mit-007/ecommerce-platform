from app.services.prompt_templete import initialize_prompt_templates,get_chat_agent_prompt

def main():

    question = "Where is my order?"

    previous_chat = [
        {
            "role": "user",
            "content": "I ordered a laptop yesterday."
        },
        {
            "role": "assistant",
            "content": "Sure, I can help you with your order."
        }
    ]

    tool_call_log = [
        {
            "tool_name": "get_order",
            "tool_args": {
                "order_id": "123"
            },
            "tool_answer": "Order ORD-123 is currently shipped."
        },
        {
            "tool_name": "get_tracking",
            "tool_args": {
                "order_id": "123"
            },
            "tool_answer": "Package is currently in Ahmedabad."
        }
    ]

    # Initialize prompt template once
    initialize_prompt_templates()

    # Render prompt with dynamic data
    prompt = get_chat_agent_prompt(
        question=question,
        previous_chat=previous_chat,
        tool_call_log=tool_call_log,
    )

    print("=" * 70)
    print("FINAL RENDERED PROMPT")
    print("=" * 70)

    print(prompt)

    print("=" * 70)


if __name__ == "__main__":
    main()
