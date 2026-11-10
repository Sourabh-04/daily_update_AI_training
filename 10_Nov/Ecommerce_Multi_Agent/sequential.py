import asyncio

from dotenv import load_dotenv
from agent_framework import AgentResponse
from agent_framework.orchestrations import SequentialBuilder

from agents import create_agents


load_dotenv()


async def main():

    # Step 1: Create agents (each already has its own tools attached)
    inventory_agent, pricing_agent, recommendation_agent = create_agents()

    # Step 2: Build the sequential workflow
    # Customer Request -> Inventory -> Pricing -> Recommendation
    # SequentialBuilder passes the full conversation to each next agent.
    workflow = SequentialBuilder(
        participants=[
            inventory_agent,
            pricing_agent,
            recommendation_agent
        ],
        output_from="all"
    ).build()

    # Step 3: Get the customer request
    question = input("Customer: ").strip()

    if not question:
        return

    # Step 4: Execute the workflow asynchronously
    result = await workflow.run(question)

    # Step 5: Display intermediate results of all three agents
    final_name, final_text = None, None

    for output in result.get_outputs():

        if not isinstance(output, AgentResponse):
            continue

        for message in output.messages:

            # Skip tool-call messages that have no text
            if not message.text or not message.text.strip():
                continue

            name = message.author_name or "Agent"
            print(f"\n========== {name} ==========")
            print(message.text)

            final_name, final_text = name, message.text

    # Step 6: Display the final recommendation (last agent's answer)
    print("\n" + "=" * 50)
    print("FINAL RECOMMENDATION")
    print("=" * 50)

    if final_name == "RecommendationAgent":
        print(final_text)
    else:
        print("No recommendation was produced.")


if __name__ == "__main__":
    asyncio.run(main())
