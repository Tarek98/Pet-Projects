"""
Day 2 — Minimal MCP server with HR-style tools.
Run: uv run hr_server.py  (or python hr_server.py)
Test with MCP Inspector or add to Cursor MCP config.
"""
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "hr-tools",
    description="HR policy and leave tools for agent prep",
)


@mcp.tool()
def get_leave_balance(employee_id: str = "me") -> str:
    """Get annual and sick leave balance for an employee.
    Args:
        employee_id: Employee ID or 'me' for current user.
    """
    return (
        f"Leave balance for {employee_id}: "
        "Annual: 12 days. Sick: 8 days. Carryover approved: 3 days."
    )


@mcp.tool()
def get_policy_snippet(topic: str) -> str:
    """Look up HR policy by topic (leave, expense, approval).
    Args:
        topic: One of: leave, expense, approval.
    """
    t = topic.lower()
    if "leave" in t:
        return "Annual leave: 15 days/year. Carryover up to 5 days if approved by manager before Dec 15."
    if "expense" in t:
        return "Submit within 30 days. Receipts required over $25. Travel over $500 needs pre-approval."
    if "approval" in t:
        return "Leave >5 days: manager approval. Expenses >$1000: manager + finance. Processed within 5 business days."
    return f"No policy found for '{topic}'. Try: leave, expense, approval."


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
