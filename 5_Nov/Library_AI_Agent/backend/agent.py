
"""Library AI Agent - terminal version.

Run: python agent.py   (the same logic is used by server.py for the web UI)
"""
from agent_core import confirm_reservation, handle_message

print("\nReady! Ask about books or reserve one (exit to stop).")

while True:
    question = input("\nYou: ").strip()
    if question.lower() == "exit":
        break
    if not question:
        continue

    response = handle_message(question)
    if response["tool_used"]:
        print(f"[Tool used: {response['tool_used']}]")
    print("AGENT:", response["reply"])

    # Terminal version of the Confirm / Cancel buttons
    if response["needs_confirmation"]:
        answer = input("Confirm reservation? (yes/no): ").strip().lower()
        pending = response["pending"]
        response = confirm_reservation(pending["book_id"], pending["customer_name"],
                                       confirmed=answer in ("y", "yes"))
        print("AGENT:", response["reply"])