"""
Day 2 — Simple agent with tools (ReAct-style).
Simulates HR/Finance-style tools: leave balance, policy lookup, expense guidelines.
Run from starter_project/: python agent_simple.py
Requires: .env with ANTHROPIC_API_KEY
"""
import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

# --- Mock HR/Finance tools (in production these would call real APIs) ---

@tool
def get_leave_balance(
    employee_id: Annotated[str, "Employee ID or 'me' for current user"],
) -> str:
    """Get current annual and sick leave balance for an employee."""
    # Simulated response
    return (
        f"Leave balance for {employee_id}: "
        "Annual leave: 12 days remaining. Sick leave: 8 days remaining. "
        "Carryover: 3 days approved for next year."
    )


@tool
def lookup_policy(
    topic: Annotated[str, "Policy topic, e.g. 'leave', 'expense', 'approval'"],
) -> str:
    """Look up company policy by topic. Use for leave, expenses, or approval rules."""
    topic_lower = topic.lower()
    if "leave" in topic_lower or "annual" in topic_lower:
        return "Policy: 15 days annual leave per year. Up to 5 days carryover if approved by manager before Dec 15."
    if "expense" in topic_lower or "reimbursement" in topic_lower:
        return "Policy: Submit expenses within 30 days. Receipts required over $25. Travel over $500 needs pre-approval. Meals up to $50/day for business travel."
    if "approval" in topic_lower:
        return "Policy: Leave over 5 days needs manager approval. Expenses over $1000 need manager and finance approval. Processing within 5 business days."
    return f"No specific policy found for '{topic}'. Try: leave, expense, approval."


@tool
def search_expense_guidelines(
    query: Annotated[str, "What you want to know about expenses, e.g. 'receipts' or 'travel limit'"],
) -> str:
    """Search expense and reimbursement guidelines."""
    q = query.lower()
    if "receipt" in q:
        return "Receipts required for any expense over $25."
    if "travel" in q or "limit" in q or "500" in q:
        return "Travel expenses over $500 require pre-approval. Meals reimbursable up to $50 per day for business travel."
    if "submit" in q or "day" in q:
        return "Expenses must be submitted within 30 days of the expense date."
    return "Expense guidelines: submit within 30 days, receipts over $25, travel over $500 pre-approved, meals $50/day."


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in .env to run this demo.")
        return

    tools = [get_leave_balance, lookup_policy, search_expense_guidelines]
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an HR/Finance assistant. Use the tools to answer questions about leave balance, policies, and expenses. Be concise."),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("Agent demo — HR/Finance tools (Ctrl+C to exit)\n")
    print("Example: 'What is my leave balance and can I carry over days?'\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            result = executor.invoke({"input": user_input})
            print(f"\nAssistant: {result['output']}\n")
        except KeyboardInterrupt:
            print("\nBye.")
            break


if __name__ == "__main__":
    main()
