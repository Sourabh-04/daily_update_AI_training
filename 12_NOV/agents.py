import asyncio
import json
import os
from pathlib import Path
from typing import Never

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agent_framework import (
    Agent,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.openai import OpenAIChatClient


PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

POLICY = (PROJECT_DIR / "policy.md").read_text(encoding="utf-8")

chat_client = OpenAIChatClient(
    model=os.environ["AZURE_OPENAI_MODEL"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    base_url=os.environ["AZURE_OPENAI_BASE_URL"],
)

eligibility_Agent = Agent(
        client=chat_client,
        
        name="elliAgent",
        instructions=f"""You review e-commerce return requests against company policy.

Company policy:
{POLICY}

Check: delivery date, invoice availability, product condition, supporting evidence.
Provide: 1. Eligibility result "True | False"  2. Explanation  3. Any exceptions""",
    )


risk_agent = Agent(
        client=chat_client,
        name="riskAgent",
        instructions="""You are the Risk Assessment Agent for an e-commerce returns workflow.
Company policy:
""" + POLICY + """

Analyze previous returns in 90 days, missing invoice/evidence, high value,
unusual behaviour and inconsistencies. Classify as LOW, MEDIUM or HIGH.
The user message contains the return request and the eligibility findings.
Return ONLY the raw JSON object. No markdown, no code fences, no text before or after it:
{"risk_level": "LOW | MEDIUM | HIGH", "risk_factors": [], "reason": "short explanation"}""",
)



    # -------------------------------------------------
    # AGENT 3: RESOLUTION AGENT
    # -------------------------------------------------

resolution_agent = Agent(
        client=chat_client,
        name="ResolutionAgent",
        instructions="""You are the Customer Response Agent.
The user message contains the final decision, eligibility summary and risk summary.
Rules:
- Be polite and concise. Do not mention internal risk evaluations or AI systems.
- Do not claim a refund/replacement/return has already been processed.
- If AUTO_APPROVED: say it is approved for processing and next steps will follow.
- If ESCALATE_FOR_HUMAN_REVIEW: say it needs additional review and they will be updated.
Return only the customer message.""",
)



def evaluate_return(req, risk_level):
    condition = req["item_condition"].upper()
    qualifies = (
        req["amount_inr"] < 25000
        and req["days_since_delivery"] <= 30
        and req["invoice_available"]
        and (condition == "UNOPENED"
             or (condition == "DAMAGED" and req["photo_evidence_available"]))
        and req["previous_returns_90_days"] < 3
        and risk_level != "HIGH"
    )
    return "AUTO_APPROVED" if qualifies else "ESCALATE_FOR_HUMAN_REVIEW"


async def main():
    requests = json.loads((PROJECT_DIR / "returns.json").read_text(encoding="utf-8"))
    req = requests[0]                      # only RET201 for now

    result = await eligibility_Agent.run(json.dumps(req))

    risk_input = {
        'return_requets': req,
        "eligibility_findings": result.text,
    }
    risk_result = await risk_agent.run(json.dumps(risk_input))
    
    print("RISK:", risk_result.text)

    risk_data = json.loads(risk_result.text)      # text -> Python dict
    risk_level = risk_data["risk_level"]          # e.g. "LOW"

    decision = evaluate_return(req, risk_level)

    print("DECISION:", decision)

    final_Input = {
        "input":risk_input,
        "risk_anamlysis":risk_data,
        "decision":decision
    }

    final_resut = await resolution_agent.run(json.dumps(final_Input))

    


    print(final_resut.text)


if __name__ == "__main__":
    asyncio.run(main())
