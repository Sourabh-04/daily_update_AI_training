# E-commerce Returns Workflow

A multi-agent workflow that reviews product return requests. AI agents check eligibility and risk, fixed Python rules make the decision, a human manager reviews anything that can't be auto-approved, and a final agent writes the customer message.

Built with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) and Azure OpenAI.

## How it works

```
return request
     │
     ▼
[1] Eligibility agent ──► explains whether the request meets the policy
     │
     ▼
[2] Risk agent ──► risk level LOW / MEDIUM / HIGH (JSON)
     │
     ▼
[3] Approval gateway ──► Python rules (evaluate_return)
     │        │
     │        └─ not auto-approved ──► PAUSE ──► manager types approve / reject ──► resume
     ▼
[4] Resolution agent ──► polite customer-facing message
```

**Why both agents and Python rules?**
- The **Python rules** handle the hard checks (amount, days, invoice, condition, previous returns). They always give the same answer and are easy to audit.
- The **agents** handle what code can't: judging risk from the request as a whole, explaining the decision, and writing the customer message.
- The **final decision is always made in Python**, never by an LLM.

## Auto-approval policy

A request is auto-approved only when **all** of these are true (see [policy.md](policy.md)):

1. Amount is below ₹25,000
2. Return is within 30 days of delivery
3. Invoice is available
4. Item is unopened, or damaged with photo evidence
5. Fewer than 3 returns in the last 90 days
6. The risk agent did not rate it HIGH

Anything else goes to a human manager.

## Possible decisions

| Decision | Meaning |
|---|---|
| `AUTO_APPROVED` | Passed every rule, no human needed |
| `MANAGER_APPROVED` | Escalated, then approved by the manager |
| `MANAGER_REJECTED` | Escalated, then rejected by the manager |

## Project structure

| File | Purpose |
|---|---|
| `agents.py` | Chat client, the three agents, and `evaluate_return()` |
| `workflow.py` | Workflow steps, approval gateway with human review, and `main()` |
| `policy.md` | Return policy given to the agents |
| `returns.json` | 10 sample return requests |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for the required settings |
| `example_output.txt` | Output from a real run |

## Setup

Requires Python 3.11 or newer and an Azure OpenAI deployment.

```bash
git clone <repo-url>
cd <repo-folder>

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your values:

```
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_BASE_URL=https://<your-resource>.openai.azure.com/openai/v1/
AZURE_OPENAI_MODEL=your-deployment-name
```

`AZURE_OPENAI_MODEL` is the **deployment name** from Azure, not the model family name. Never commit your `.env` file.

## Run

```bash
python workflow.py
```

The workflow processes the requests from `returns.json` one by one. When a request needs review, it pauses and asks:

```
RET202 needs review. approve / reject?
```

Type `approve` or `reject` and the workflow continues to write the customer message.

See [example_output.txt](example_output.txt) for a real run: one auto-approved request and one rejected by the manager.

## Expected results for the sample data

| Request | Product | Result | Reason |
|---|---|---|---|
| RET201 | Wireless Keyboard | Auto-approved | Meets all rules |
| RET202 | Gaming Laptop | Manager review | Above ₹25,000, used |
| RET203 | Ceramic Dinner Set | Auto-approved | Damaged with photos |
| RET204 | Travel Suitcase | Manager review | Damaged, no photo |
| RET205 | Yoga Mat | Manager review | 44 days since delivery |
| RET206 | Desk Lamp | Manager review | 4 previous returns |
| RET207 | Coffee Grinder | Manager review | No invoice |
| RET208 | Sketchbook Set | Auto-approved | Meets all rules |
| RET209 | Smartwatch | Manager review | Item used |
| RET210 | Floor Mirror | Auto-approved | Damaged with photos |

Requests marked auto-approved still go to manager review if the risk agent rates them HIGH.

## Notes

- If the risk agent's answer can't be read as JSON, the request is treated as HIGH risk and sent to a human, never auto-approved.
- `main()` currently runs a slice of `returns.json`. Change the slice in the `for` loop to run more requests.
