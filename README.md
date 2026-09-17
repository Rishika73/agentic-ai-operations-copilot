# Agentic AI Operations Copilot

Multi-agent AI operations copilot built with LangGraph, OpenAI, MCP, semantic retrieval, SQLite checkpointing, tool calling, and human-in-the-loop approvals.

## Overview

This project demonstrates how an AI operations copilot can route operational questions to specialized agents, retrieve relevant internal knowledge, inspect customer and incident data, propose operational actions, and require human approval before executing higher-impact workflows.

The current implementation focuses on three operational domains:

- Incident management
- Customer/account risk
- Operations knowledge and policy retrieval

## Key Features

### Multi-Agent Workflow

The LangGraph workflow routes user requests to specialized agents:

- `incident_agent` — analyzes open support incidents
- `account_risk_agent` — identifies high-risk customer accounts and renewal risk
- `knowledge_agent` — retrieves operational policies and guidance

The router distinguishes between operational incidents, account-risk questions, and knowledge/policy requests.

### Semantic RAG

The knowledge agent uses OpenAI embeddings with cosine similarity to retrieve relevant entries from the local operations knowledge base.

Current embedding model:

```text
text-embedding-3-small
