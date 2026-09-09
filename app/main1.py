import asyncio
from app.agent.graph import agent
from app.services.llm_service import initialize_llm
from app.services.prompt_templete import initialize_prompt_templates

_previous_chat = []

async def main():

    await initialize_llm()
    initialize_prompt_templates()
    
    print("\n🤖 AI Agent Started")
    print("Type 'exit' to quit.\n")

    while True:

        print("----------------")
        print("|👤 Question : |")
        print("----------------\n")

        question = input("-> : ").strip()

        if question.lower() == "exit":
            print("👋 Goodbye!")
            break

        if not question:
            continue

        try:
            response = await agent.ainvoke(
                {
                    "question": question,
                    "tool_call_log": [],
                    "previous_chat": _previous_chat,
                },
            )

            # Show tool calls
            print("\n\n------------------------")
            print("| Tool Call Log :      |")
            print("------------------------\n")
            for tool in response.get("tool_call_log", []):
                print(f"\n🔧 Tool: {tool['tool_name']}")
                print(f"   Args: {tool['tool_args']}")
                print(f"   Result: {tool['tool_answer']}")
                print("\n-------------------------------------------------------------------------------------------------------------\n")

            # Show AI response
            answer = response["final_answer"].content[0]['text']


            print("\n\n---------------------")
            print("| 🤖  Ai :          |")
            print("---------------------\n")
            print(f" <- : {answer}\n\n")

            new_messages_list = [
                {
                    "role" : "user",
                    "content" : question
                },
                {
                    "role" : "AI",
                    "content" : answer
                }
            ]

            _previous_chat.extend(new_messages_list)
            # print(_previous_chat)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())