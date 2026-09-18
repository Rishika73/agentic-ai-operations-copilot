# Agentic AI Operations Copilot

Multi-agent AI operations copilot built with LangGraph, OpenAI, MCP, semantic retrieval, SQLite checkpointing, FastAPI, Docker, GitHub Actions, and human-in-the-loop approvals.

## Overview

This project routes operational questions to specialized agents, retrieves internal knowledge, inspects incident and customer data, proposes operational actions, and requires human approval before higher-impact workflows are executed.

The current implementation covers:

- Incident management
- Customer/account risk
- Operations knowledge and policy retrieval

## Key Features

### Multi-Agent Workflow

LangGraph routes requests to three specialized agents:

- `incident_agent` — analyzes open support incidents
- `account_risk_agent` — identifies high-risk customer accounts and renewal risk
- `knowledge_agent` — retrieves operational policies and guidance

### Semantic RAG

The knowledge agent uses OpenAI embeddings and cosine similarity for semantic retrieval.

Embedding model:

```text
text-embedding-3-small
```

This allows semantically similar queries to retrieve the relevant operational guidance even when the wording differs.

### MCP Server

The project includes a working Model Context Protocol server.

Available MCP tools:

```text
open_incidents
at_risk_accounts
accounts_renewing_within
search_operations_knowledge
```

The MCP server has been verified using MCP Inspector.

### Human-in-the-Loop Approval

Higher-impact operational actions require explicit human approval.

Examples:

- Incident escalation
- Customer-success outreach

LangGraph `interrupt()` pauses execution until an action is approved or rejected.

Knowledge-only requests do not require approval.

### Persistent Workflow State

LangGraph checkpoint state is persisted using SQLite.

```text
agent_memory.db
```

This allows interrupted workflows to resume using the same thread ID.

SQLite database and runtime files are excluded from Git.

## FastAPI Service

Start the API:

```bash
PYTHONPATH=. uvicorn app.main:app --reload
```

Available endpoints:

```text
GET  /
GET  /health
POST /ask
POST /approve
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"What open incidents do we have?"}'
```

Operational requests requiring approval return:

```text
status: awaiting_approval
```

The workflow can then be resumed through `/approve` using the returned `thread_id`.

## Architecture

```text
User Query
    |
    v
LangGraph Router
    |
    +-------------------+--------------------+
    |                   |                    |
    v                   v                    v
Incident Agent     Account Risk Agent   Knowledge Agent
    |                   |                    |
Ticket Tools          CRM Tools        Semantic RAG
    |                   |                    |
    +-------------------+--------------------+
                        |
                        v
                 Action Proposal
                        |
                        v
              Human Approval Gate
                        |
                 approve / reject
                        |
                        v
                 Action Execution
```

## Project Structure

```text
agentic-ai-operations-copilot/
├── agents/
│   ├── incident_agent.py
│   ├── account_risk_agent.py
│   └── knowledge_agent.py
├── app/
│   ├── actions.py
│   ├── agent_graph.py
│   ├── llm.py
│   ├── main.py
│   └── state.py
├── tools/
│   ├── crm_tool.py
│   ├── ticket_tool.py
│   └── knowledge_tool.py
├── data/
│   ├── customer_accounts.json
│   ├── operations_knowledge.json
│   └── support_tickets.json
├── tests/
│   ├── test_actions.py
│   ├── test_agent_graph.py
│   ├── test_api.py
│   └── test_knowledge_tool.py
├── evals/
├── docs/
├── .github/
│   └── workflows/
│       └── tests.yml
├── mcp_server.py
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`.

Do not commit `.env`.

## Run the CLI

```bash
PYTHONPATH=. python -u app/agent_graph.py
```

Example prompts:

```text
What open incidents do we have?
Which customer accounts are at risk?
What is the policy for critical incident response?
```

## MCP Usage

Start the MCP server:

```bash
PYTHONPATH=. python -u mcp_server.py
```

Run MCP Inspector:

```bash
mcp dev mcp_server.py
```

## Docker

Build the image:

```bash
docker build -t agentic-ai-operations-copilot .
```

Run the container:

```bash
docker run --rm -it \
  --env-file .env \
  agentic-ai-operations-copilot
```

## Testing

Run the complete test suite:

```bash
PYTHONPATH=. python -m pytest -q
```

Current verified local result:

```text
19 passed
```

Test coverage includes:

- Agent routing
- Human approval behavior
- Safe action execution
- Semantic knowledge retrieval
- Similarity scoring and top-k retrieval
- FastAPI health endpoint
- FastAPI `/ask` endpoint
- FastAPI approval workflow

## CI

GitHub Actions automatically runs the test suite on pushes and pull requests to `main`.

## Tech Stack

- Python
- LangGraph
- OpenAI API
- OpenAI Embeddings
- Model Context Protocol (MCP)
- FastAPI
- SQLite
- NumPy
- Pytest
- Docker
- GitHub Actions

## Current Scope

The project uses synthetic JSON datasets for incidents, customer accounts, and operational knowledge.

Semantic retrieval uses an in-process embedding index suitable for this demonstration dataset.

Operational execution is simulated through structured action results. The project does not directly modify production systems or contact real customers.

## Future Improvements

- Persistent vector database
- Hybrid retrieval and reranking
- Observability and tracing
- Larger evaluation suite
- External operational-system integrations
- Deployment
