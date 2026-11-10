import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from agent_framework.openai import OpenAIChatCompletionClient


from tools import search_products, calculate_order_total 

def create_agents():

    # Shared model client
        # Shared model client (OpenRouter)
    client = OpenAIChatCompletionClient(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )


    # Agent 1: Inventory Agent
    inventory_agent = Agent(
        client=client,
        name="InventoryAgent",
        instructions=(
            "You are an inventory specialist for an electronics store. "
            "Understand what product the customer wants (type, brand/name, "
            "and any budget or quantity they mention). "
            "Use search_products to find matching products. Search with a "
            "singular category (e.g. 'Laptop', not 'laptops') or a product name. "
            "If the first search finds nothing, try one related term. "
            "List every matching product with its ID, name, price (INR), "
            "stock and rating, and clearly mark items that are out of stock. "
            "End with a short summary for the next agent: the customer's "
            "requested quantity and budget (if given) and the product IDs "
            "that are in stock. "
            "Only use data returned by the tool. Never invent products, "
            "prices or stock. Do not calculate order totals."
        ),
        tools=[search_products]
    )

    # Agent 2: Pricing Agent
    pricing_agent = Agent(
        client=client,
        name="PricingAgent",
        instructions=(
            "You are a pricing specialist for an electronics store. "
            "Read the customer's request and the Inventory Agent's results "
            "from the conversation. "
            "For each in-stock product the Inventory Agent listed, call "
            "calculate_order_total with its product ID and the customer's "
            "requested quantity (use 1 if no quantity was given). "
            "The tool checks stock: if it reports insufficient stock, out of "
            "stock, an invalid quantity or an unknown product, report that "
            "and exclude the product. "
            "Compare each verified total with the customer's budget, if one "
            "was given, and label each product 'Within budget' or "
            "'Over budget' with the amount over. "
            "End with a short summary listing the affordable product IDs "
            "with their verified totals for the next agent. "
            "Only use totals returned by the tool. Never calculate or invent "
            "prices yourself, and do not make the final recommendation."
        ),
        tools=[calculate_order_total]
    )

    # Agent 3: Recommendation Agent
    recommendation_agent = Agent(
        client=client,
        name="RecommendationAgent",
        instructions=(
            "You are a product recommendation specialist for an electronics "
            "store. Review the customer's request and the Inventory and "
            "Pricing Agents' results from the conversation. "
            "Consider only products that are in stock for the requested "
            "quantity and whose verified total is within the customer's "
            "budget. Never recommend out-of-stock, insufficient-stock or "
            "over-budget products. "
            "From those, recommend the single product with the highest "
            "rating. If ratings are equal, choose the one with the lower "
            "total cost. "
            "Give the product ID, name, rating, quantity and verified total, "
            "followed by a short 1-2 sentence explanation of why it was "
            "chosen. "
            "If no product meets the requirements, say so clearly and "
            "explain why (e.g. over budget or out of stock). "
            "Use only data from the previous agents. Never invent products, "
            "ratings or prices."
        )
    )

    return inventory_agent, pricing_agent, recommendation_agent


