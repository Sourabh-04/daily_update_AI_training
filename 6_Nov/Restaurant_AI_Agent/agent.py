import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from tools import search_restaurants, calculate_dining_cost

# STEP 1: Load environment (.env must contain OPENROUTER_API_KEY)
load_dotenv()

# STEP 2: Create model
# OpenRouter speaks the OpenAI API, so ChatOpenAI works with a different base_url.
model = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "liquid/lfm-2.5-2.6b:free"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)

# STEP 3: Create agent
agent = create_agent(
    model=model,
    tools=[
        search_restaurants,
        calculate_dining_cost,
    ],
    system_prompt=(
        "You are a Restaurant AI Assistant. "
        "Only answer questions about the available restaurants, "
        "their cuisines, locations, prices and seat availability, "
        "and estimated dining costs. "
        "Use search_restaurants to find restaurants by cuisine or name. "
        "Call search_restaurants with a single keyword, such as a cuisine "
        "or restaurant name (e.g. 'Indian' or 'Spice Garden'), not a full sentence. "
        "Use calculate_dining_cost to estimate the total cost for a group. "
        "calculate_dining_cost needs the restaurant ID, so search first "
        "if the user only gives a name or cuisine. "
        "If the user has not said how many guests, ask before calculating. "
        "Remember the selected restaurant during the conversation. "
        "All prices are in Indian Rupees (Rs). "
        "Never invent restaurant names, IDs, prices or seat counts; "
        "only use what the tools return. "
        "If a tool returns an error, tell the user about it. "
        "Never calculate costs yourself; always use calculate_dining_cost. "
        "If a restaurant has fewer available seats than the number of guests, "
        "tell the user. "
        "You cannot make reservations or take payments. If the user asks to "
        "book or pay, say: 'I can't make bookings or payments, but I can "
        "help you find a restaurant and estimate the cost.' "
        "For unrelated questions, say: "
        "'I can only help with restaurants and dining costs.'"
    ),
    checkpointer=InMemorySaver()
)

# STEP 4: Run application
if __name__ == "__main__":

    thread_number = 1
    previous_count = 0

    print("LangChain Restaurant AI Agent")
    print("Type /new for a new conversation")
    print("Type exit to quit")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            break

        if question.lower() == "/new":
            thread_number += 1
            previous_count = 0
            print("New conversation started.")
            continue

        if not question:
            continue

        config = {
            "configurable": {
                "thread_id": f"restaurant-{thread_number}"
            }
        }

        try:
            result = agent.invoke(
                {
                    "messages": [
                        {"role": "user", "content": question}
                    ]
                },
                config=config
            )

            messages = result["messages"]
            new_messages = messages[previous_count:]
            previous_count = len(messages)

            # Show which tools the agent called (useful for learning/debugging)
            for message in new_messages:

                if isinstance(message, AIMessage):
                    for call in message.tool_calls:
                        print("[TOOL]:", call["name"])
                        print("Arguments:", call["args"])

                if isinstance(message, ToolMessage):
                    print("[TOOL RESULT]:", message.content)

            print("\nAgent:", messages[-1].content)

        except Exception as error:
            print("Error:", error)
