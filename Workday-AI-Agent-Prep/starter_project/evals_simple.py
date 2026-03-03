"""
Day 3 — Simple agentic evals: run the agent on a few golden prompts and check
that the right tools were used or key content appears in the output.
Run from starter_project/: python evals_simple.py
Requires: .env with OPENAI_API_KEY, and agent_simple's tools/agent.
"""
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

# Reuse the same tools and agent setup as agent_simple
from agent_simple import get_leave_balance, lookup_policy, search_expense_guidelines

load_dotenv()


def build_executor():
    tools = [get_leave_balance, lookup_policy, search_expense_guidelines]
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an HR/Finance assistant. Use the tools to answer. Be concise."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)


# Golden set: (prompt, list of substrings that should appear in output OR tool names that should be called)
GOLDEN = [
    {
        "prompt": "What is my leave balance?",
        "output_contains": ["leave", "12"],  # expect "12 days" or similar
        "tools_used": ["get_leave_balance"],
    },
    {
        "prompt": "What is the policy on expense receipts?",
        "output_contains": ["25", "receipt"],  # receipts over $25
        "tools_used": ["lookup_policy", "search_expense_guidelines"],
    },
    {
        "prompt": "How many days can I carry over?",
        "output_contains": ["5", "carry"],  # up to 5 days carryover
        "tools_used": [],  # optional: could require lookup_policy
    },
]


def run_evals():
    if not os.getenv("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY in .env to run evals.")
        return

    executor = build_executor()
    results = []

    for i, case in enumerate(GOLDEN):
        prompt = case["prompt"]
        output_contains = case.get("output_contains", [])
        tools_expected = set(case.get("tools_used", []))

        result = executor.invoke({"input": prompt})
        output = result.get("output", "").lower()
        steps = result.get("intermediate_steps", [])
        tools_used = set()
        for step in steps:
            if len(step) >= 1 and hasattr(step[0], "tool"):
                tools_used.add(step[0].tool)

        # Check output content: all required substrings must appear
        content_ok = all(s.lower() in output for s in output_contains) if output_contains else True

        # Check tools (at least one expected tool was used if we specified any)
        tools_ok = (tools_used >= tools_expected) if tools_expected else True

        passed = content_ok and tools_ok
        results.append({
            "prompt": prompt,
            "passed": passed,
            "output_snippet": output[:200] + "..." if len(output) > 200 else output,
            "tools_used": list(tools_used),
            "content_ok": content_ok,
            "tools_ok": tools_ok,
        })

    # Report
    print("Agentic evals — golden set\n")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['prompt']}")
        print(f"  Tools used: {r['tools_used']}")
        if not r["content_ok"]:
            print("  (output missing expected content)")
        if not r["tools_ok"]:
            print("  (expected tools not all used)")
        print()

    passed_count = sum(1 for r in results if r["passed"])
    print(f"Result: {passed_count}/{len(results)} passed.")
    return results


if __name__ == "__main__":
    run_evals()
