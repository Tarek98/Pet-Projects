# Workday AI Agent Engineering — 3-Day Prep Plan

A focused learning plan aligned with the **AI Agent Engineering** role at Workday (HR & Finance AI agents, full stack, “you build it you run it”) and the topics recommended from your interviews: **Cursor IDE**, **RAG**, **LangChain**, **MCP**, **multi-agent orchestration**, and **Agentic AI evals**.

---

## Role snapshot (from the posting)

- **Team:** AI Agent Engineering — HR & Finance AI agents deeply integrated in the Workday suite.
- **You’ll:** Build AI-powered agents for HR/Financial workflows, own multiple areas from dev to production, and contribute to tooling and platform growth.
- **Tech:** Python (Flask/Django/FastAPI), React + TypeScript, PostgreSQL, AWS, Docker/Kubernetes, Elasticsearch; DevOps, CI/CD, observability.

This plan prioritizes **agent concepts and tooling** so you can speak to the stack and extend the starter project in your first weeks.

---

## 3-day schedule (high level)

| Day | Focus | Outcomes |
|-----|--------|----------|
| **1** | Cursor IDE + RAG fundamentals | Cursor workflows, RAG flow (chunk → embed → retrieve → generate), run the starter RAG example |
| **2** | LangChain + MCP + multi-agent | Chains, tools, agent; minimal MCP server; LangGraph/CrewAI concepts |
| **3** | Agentic AI evals + integration | What to measure (tool use, task completion, safety), evals mindset; tie the project together |
| **4 (bonus)** | Hiking Trip Planner | Multi-agent: Explorer (geocode, weather, trails) → Planner (itinerary + social post) |

---

## Day 1 — Cursor IDE + RAG

### Cursor IDE (≈1–2 hours)

- **Use Cursor as your primary editor** for this repo so all practice is in-context.
- **@-mentions:** Reference files (`@filename`), folders (`@folder/`), and docs so the AI has codebase context.
- **Chat vs Agent:** Use **Chat** for questions and small edits; use **Agent** for multi-file changes and “implement X” tasks.
- **Rules:** Skim `.cursor/rules` or project rules if present; they steer style and patterns.
- **Terminal:** Run and debug from Cursor (e.g. `uv run` or `python` for the prep project).

### RAG fundamentals (≈2–3 hours)

**Concepts:**

1. **Why RAG:** LLMs don’t have your private data (HR policies, finance docs). RAG = Retrieve (from your store) + use as context when you Generate.
2. **Pipeline:** Documents → chunking → embeddings → vector store → on query: embed query → retrieve top-k chunks → pass as context to LLM → generate answer.
3. **Chunking:** Size/overlap tradeoff; often 512–1024 tokens with overlap. Semantic boundaries (e.g. by section) often beat fixed size.
4. **Retrieval:** Similarity search (cosine or dot product); optional reranking for quality.

**Hands-on in this repo:**

- Run the RAG example in `starter_project/` (see below).
- Change chunk size or top-k and see how answers change.
- Add a small “HR policy” or “expense policy” text file and ingest it; ask questions and verify retrieval is used.

**Optional read:** [LangChain RAG tutorial](https://python.langchain.com/docs/tutorials/rag/) (focus on the flow, not every API).

---

## Day 2 — LangChain + MCP + multi-agent

### LangChain: chains, tools, and agents (≈2–3 hours)

- **Chain:** Composed sequence of steps (e.g. prompt → model → parser). In LangChain, use **LCEL** (`|` operator). Example: `prompt | llm | StrOutputParser()`.
- **Tool:** A function the model can call (name, description, args schema). LangChain uses `@tool` and Pydantic. **Agent:** loop of model → tool call → result → repeat until final answer (ReAct-style).
- **Hands-on:** Run and modify `starter_project/agent_simple.py` (system message, user message). Use the 2–3 tools to answer a multi-step question (e.g. “What’s my leave balance and what does the policy say about carryover?”).
- **Docs:** [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/), [Agents](https://python.langchain.com/docs/concepts/agents/).

### MCP (Model Context Protocol) (≈1–1.5 hours)

- **What:** Open protocol so any client (e.g. Cursor) can discover and call **tools** and **resources** from a server — “USB-C for AI.”
- **Hands-on:** `starter_project/mcp_server_hr/` has a minimal MCP server (`get_leave_balance`, `get_policy_snippet`). To run it:

  ```bash
  pip install "mcp[cli]"
  cd starter_project/mcp_server_hr && uv run hr_server.py   # or python hr_server.py
  ```

  Test with [MCP Inspector](https://github.com/modelcontextprotocol/inspector) or add the server to Cursor’s MCP config.
- **Docs:** [modelcontextprotocol.io](https://modelcontextprotocol.io) — “Build an MCP server”.

### Multi-agent orchestration (≈30–60 min)

- **Idea:** Multiple specialized agents coordinated by a supervisor or a graph. **Frameworks:** **LangGraph** (state, checkpointing, production), **CrewAI** (role-based crews), **AutoGen** (conversation patterns).
- **Today:** Don’t build a full multi-agent app. Skim one “LangGraph quickstart” or “CrewAI intro”; understand **supervisor vs. graph** and **when to add more agents**.

---

## Day 3 — Agentic AI evals + integration

### Agentic AI evals (≈1.5–2 hours)

- **Difference from “normal” LLM evals:** You care about **tool use** (correctness, efficiency), **task completion** (end-to-end workflow success), **safety** (no harmful tool calls), and **instruction following** (constraints, steps).
- **What to measure (high level):**
  - **Tool use:** Right tool chosen? Correct arguments? Minimal unnecessary calls?
  - **Task completion:** Did the agent achieve the user’s goal (e.g. “book leave and notify manager”)?
  - **Agentic reasoning:** Planning, multi-step reasoning, handling failures.
  - **Cost/latency:** Token usage, number of steps, time to completion.
- **Mindset:** Evals are tests for agent behavior. Start with a small set of “golden” user queries and expected behavior (e.g. which tools should be called, what the final answer should contain). Automate checks where possible (e.g. “response must include X” or “must have called tool Y”).
- **Optional:** Skim [“LLM Agent Evaluation”](https://confident-ai.com/blog/llm-agent-evaluation-complete-guide) or the “Agentic AI Benchmark” papers for vocabulary you might hear in team discussions.

### Integration (≈1–2 hours)

- **Starter project:** Add one “eval”: 3–5 fixed prompts and a simple script that runs the agent and checks (e.g. string or JSON) that the right tools were used or key facts appear.
- **Recap:** Walk through your RAG pipeline, your agent’s tools, and your eval script. Be ready to explain “I’d add more evals for edge cases and production monitoring.”

---

## Day 4 (bonus) — Multi-agent: Hiking Trip Planner

A fun multi-agent demo that suggests trails near your home and drafts a social post to invite friends.

- **Explorer agent:** Uses **geocoding** (Nominatim, free), **weather** (Open-Meteo, free), and mock **AllTrails-style trails** and **Google Maps–style directions** to research trails and conditions near the address you give.
- **Planner agent:** Takes that research and writes a short **trip summary** (itinerary, what to bring) and a **social media post** to invite people to the hike.

**Run it:** From the `hiking-planner/` folder with `ANTHROPIC_API_KEY` set:

```bash
cd Workday-AI-Agent-Prep/hiking-planner
pip install -r requirements.txt
python hiking_planner.py
```

Example input: *“I live at 123 Main St, Vancouver BC — suggest a trail and help me invite friends for this weekend.”*  
Trails and ETA use **mock data** so it runs without AllTrails/Google API keys; you can plug in real APIs later.

**Web UI (React + TypeScript):** In `hiking-planner/`, run the API with `uvicorn hiking_api:app --reload --port 8000`, then `cd hiking-planner-ui && npm install && npm run dev` — open http://localhost:5173 (proxies `/api` to the backend). See `hiking-planner/README.md`.

---

## Starter project in this repo

The `starter_project/` directory contains a minimal but runnable setup:

- **RAG:** Ingest a few documents (e.g. HR/expense policy), embed, store in a vector store, and answer questions.
- **LangChain agent:** A simple agent with tools (e.g. leave balance, policy lookup) to simulate HR/Finance-style workflows.
- **Structure:** FastAPI-style layout (you can add a small API later); Python 3.10+.

The **Hiking Trip Planner (Day 4 bonus)** lives in **`hiking-planner/`** (separate folder with its own requirements and Web UI).

**How to run:**

```bash
cd Workday-AI-Agent-Prep/starter_project
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env        # then add your ANTHROPIC_API_KEY
python rag_demo.py          # RAG demo (Day 1)
python agent_simple.py      # Agent with tools (Day 2)
python evals_simple.py      # Simple evals (Day 3)
```

For the **MCP server** (Day 2), see the run commands in the Day 2 — MCP section above. For the **Hiking Trip Planner** (Day 4), see `hiking-planner/README.md`.

Use this as your playground for Days 1–3: add docs, add tools, add evals, run the MCP server. Use `hiking-planner/` for the multi-agent demo.

---

## Quick reference: interview talking points

- **RAG:** “We use RAG so agents can answer from company-specific data (policies, guidelines) without fine-tuning; we tune chunking and retrieval for our docs.”
- **LangChain:** “We use LangChain for chains and tool-calling agents; we’re evaluating LangGraph for multi-step workflows and state.”
- **MCP:** “MCP gives us a standard way to expose internal APIs and data as tools so different agents and clients can reuse them.”
- **Multi-agent:** “For complex workflows we’re looking at a supervisor or graph (e.g. LangGraph) so we can have specialized agents and clear state and retries.”
- **Evals:** “We evaluate agents on tool use correctness, task completion, and safety; we’re building a small golden set and automating checks where we can.”

Good luck with your first week at Workday.
