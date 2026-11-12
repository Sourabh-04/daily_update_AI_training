import asyncio
import json
from typing import Never

from agent_framework import WorkflowBuilder, WorkflowContext, executor,handler,response_handler,Executor

from agents import (
    PROJECT_DIR,
    eligibility_Agent,
    risk_agent,
    resolution_agent,
    evaluate_return,
    OpenAIChatClient,
    chat_client,
)

class ApprovalGateway(Executor):
    def __init__(self):
        super().__init__(id="approval_gateway")
    @handler
    async def review(
        self,
        case: dict,
        ctx: WorkflowContext[dict],
    ) -> None:

            decision = evaluate_return(case, case["risk_level"])
            if decision == "AUTO_APPROVED":
                 print("[3/4] Decision   : AUTO_APPROVED")

                 await ctx.send_message({**case, "decision": decision})
                 return
            
            print("[3/4] Decision   : ESCALATED -> needs manager review")
            print("-" * 60)
            print("  MANAGER REVIEW REQUIRED")
            print(f"  Product : {case['product']}  (₹{case['amount_inr']})")
            print(f"  Risk    : {case['risk_level']}")
            print("-" * 60)


            print("  ApprovalGateway: PAUSED - awaiting manager")
            await ctx.request_info(request_data=case, response_type=str)


    @response_handler
    async def on_manager_decision(
        self,
        case: dict,
        response:str,
        ctx: WorkflowContext[dict]
    ) -> None:
        decision = response.strip().lower()
        if decision not in {"approve", "reject"}:
            decision = "reject"

        decision = (
            "MANAGER_APPROVED"
            if decision == "approve"
            else "MANAGER_REJECTED"
        )
        print(f"[3/4] Decision   : {decision}  (by manager)")

        

        # RESUME THE WORKFLOW
        await ctx.send_message({**case, "decision":decision, "decision_by": "Human manager"})
         
         
         

                

def build_workflow(chat_client:OpenAIChatClient):

    @executor(id="ellibilty")
    async def ellibilty(
        case : dict,
        ctx : WorkflowContext[dict]
    ):
        print("[1/4] Eligibility check ... done")

        result = await eligibility_Agent.run(json.dumps(case))
        print("severity:", result.text)

        await ctx.send_message({
            **case,
            "severity": result.text,
        })

    @executor(id="risk")
    async def risk(
        case :dict,
        ctx : WorkflowContext[dict]
    ):
        risk_result = await risk_agent.run(json.dumps(case))


        
        # Keep only the part from the first { to the last } (drops ```json fences / extra text)
        text = risk_result.text
        start = text.find("{")
        end = text.rfind("}")

        try:
            risk_data = json.loads(text[start:end + 1])
            risk_level = risk_data["risk_level"].upper()
        except (json.JSONDecodeError, KeyError, AttributeError):
            print("  Could not read risk JSON -> treating as HIGH")
            risk_data = {"risk_level": "HIGH", "reason": "Risk output unreadable"}
            risk_level = "HIGH"
        print(f"[2/4] Risk level : {risk_level}")
        print(f"      Reason     : {risk_data.get('reason', '-')}")
        await ctx.send_message({
            **case,
            "risk_level" : risk_level
        })

    # @executor(id="approval_gateway")
    # async def approval_gateway(case: dict, ctx: WorkflowContext[dict]):
    #     decision = evaluate_return(case, case["risk_level"])
    #     print("DECISION:", decision)

    #     await ctx.send_message({
    #         **case,
    #         "decision": decision,
    #     })

    approval_gateway  = ApprovalGateway()
    

    @executor(id="resolution")
    async def resolution(
            case :dict,
            ctx : WorkflowContext[dict]
        ):
            resolution_result = await resolution_agent.run(json.dumps(case))
            # print("resolution:", resolution_result.text)
            
            await ctx.yield_output(resolution_result.text)


    return (
        WorkflowBuilder(start_executor=ellibilty)
        .add_chain([ellibilty, risk, approval_gateway, resolution])
        .build()
    )


async def main():
    requests = json.loads((PROJECT_DIR / "returns.json").read_text(encoding="utf-8"))
    workflow = build_workflow(chat_client)

    

    for req in requests[:2]:
        print("\n" + "=" * 60)
        print(f" {req['request_id']}  |  {req['product']}  |  ₹{req['amount_inr']}  |  {req['item_condition']}")
        print("=" * 60)


        result = await workflow.run(req)
        pending = result.get_request_info_events()
        while pending:
            event = pending[0]
            answer = input(f"{req['request_id']} needs review. approve / reject? ")
            result = await workflow.run(responses={event.request_id: answer})
            pending = result.get_request_info_events()
        print("[4/4] Customer message:")
        print("-" * 60)
        print(result.get_outputs()[0])
        print("-" * 60)



if __name__ == "__main__":
    asyncio.run(main())


    

    

