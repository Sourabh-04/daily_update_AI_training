import json
from datetime import date

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app import config
from app.tools import TOOLS


def get_llm():
    if config.LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=config.OLLAMA_MODEL, base_url=config.OLLAMA_BASE_URL, temperature=0)

    from langchain_openai import ChatOpenAI          # Goedel speaks the OpenAI API
    return ChatOpenAI(
        model=config.GOEDEL_MODEL,
        base_url=config.GOEDEL_BASE_URL,
        api_key=config.GOEDEL_API_KEY,
        temperature=0,
        extra_body={"chat_template_kwargs": {"thinking": False}},  # faster, fewer tokens
    )


llm = get_llm()
llm_with_tools = llm.bind_tools(TOOLS)
tools_by_name = {t.name: t for t in TOOLS}


# ---------- STAGE 1: gather facts with tools ----------
def gather_facts(question: str, history: list[dict], employee_id: str | None):
    system = (
        f"You collect facts for a business travel assistant. Today is {date.today()}. "
        "Use the tools to find the employee's saved trip and the weather forecast for it. "
        "Use the conversation history to understand words like 'there' or 'my trip'. "
        "Never guess trip details or weather - only use tool results."
    )
    if employee_id:
        system += f" The employee ID is {employee_id}."

    messages = [SystemMessage(system), *history, HumanMessage(question)]
    facts, tools_used = [], []

    for _ in range(5):                         # safety limit on tool rounds
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        if not ai_msg.tool_calls:              # model has everything it needs
            break
        for call in ai_msg.tool_calls:
            tool_msg = tools_by_name[call["name"]].invoke(call)   # runs the tool
            messages.append(tool_msg)
            tools_used.append(call["name"])
            facts.append({"tool": call["name"], "args": call["args"], "result": tool_msg.content})

    return facts, tools_used


# ---------- STAGE 2: write the advice from facts only ----------
advice_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a business travel advisor. Answer using ONLY the facts below.\n"
     "If a fact contains an error or the weather is missing, clearly say the data is unavailable "
     "and do NOT invent weather.\n"
     "When weather is available, give: the destination, a short weather summary "
     "(temperatures and rain), and 3-4 practical packing or travel tips. Keep it concise.\n\n"
     "FACTS:\n{facts}"),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])
advice_chain = advice_prompt | llm | StrOutputParser()


def ask(question: str, history: list[dict], employee_id: str | None = None):
    facts, tools_used = gather_facts(question, history, employee_id)                 # stage 1
    answer = advice_chain.invoke({                                                    # stage 2
        "facts": json.dumps(facts, indent=1) if facts else "No facts were retrieved.",
        "history": history,
        "question": question,
    })
    return answer, tools_used
