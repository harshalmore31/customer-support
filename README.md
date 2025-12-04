# DigitalOcean Gradient AI Agent with Memori

This repository demonstrates how to build a stateful, AI-powered customer-support agent using DigitalOcean's Gradient AI platform combined with [Memori](https://github.com/MemoriLabs/Memori), a SQL-native memory layer that automatically captures, stores, and recalls long-term user context.

The integration delivers:

- Automatic long-term memory (no manual save/recall)
- PostgreSQL-backed durable storage
- Plug-and-play support for any LLM accessible through Gradient
- OpenAI-compatible API surface for easy migration and hosting

## Overview

Traditional agents lose context between sessions. This example shows how Memori + Gradient AI closes that gap by providing:

**Persistent Memory**
Facts, preferences, entities, and relationships extracted from conversations are automatically written to PostgreSQL with no latency impact.

**Stateless Agent, Stateful Behavior**
Your Gradient AI Agent remains stateless, while Memori maintains continuity across all sessions and channels.

**Drop-in Integration**
Memori exposes an OpenAI-compatible API wrapper, so your code changes are minimal when switching from OpenAI-hosted agents to Gradient-hosted agents.


## Architecture

```
┌─────────────────────────────────────────┐
│ APPLICATION LAYER                       │
│  Your code + Gradient AI Agent          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ MEMORI CORE                             │
│  • LLM provider wrappers                │
│  • Attribution (entity/process/session) │
│  • Recall API                           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ STORAGE LAYER                           │
│  • Connection Registry                  │
│  • Database Adapters                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ PostgreSQL                              │
└─────────────────────────────────────────┘
```

### Attribution Model

Memori assigns memory at three levels so agents can reason over long-term user state:

- **Entity** - end user (customer)
- **Process** - the Gradient AI Agent
- **Session** - a single conversation/task boundary

Advanced augmentation runs asynchronously, extracting facts, preferences, relationships, and timelines with zero extra latency to the agent.

## Prerequisites

- Python 3.10+
- PostgreSQL instance (local or managed)
- DigitalOcean Gradient AI Agent Deployment (endpoint + access key)

## Installation

```bash
# Clone the repository
git clone https://github.com/harshalmore31/customer-support.git
cd customer-support

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description |
|----------|-------------|
| `AGENT_ENDPOINT` | DigitalOcean Gradient Agent endpoint URL |
| `AGENT_ACCESS_KEY` | Gradient Agent access key |

Optional configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://postgres@localhost:5432/memori-v3` |

## Usage

```bash
python gradient-agent-memori.py
```

The application will:
1. Connect to the PostgreSQL database
2. Initialize Memori storage tables
3. Connect to your Gradient AI Agent
4. Start an interactive chat session with automatic memory persistence

## Project Structure

```
.
├── gradient-agent-memori.py    # Main application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── archives/                  # Legacy implementations
```

## Integration Details

### Memori Configuration

```python
from memori import Memori

mem = Memori(conn=db_session_factory)
mem.attribution(entity_id="user_id", process_id="gradient_agent")
mem.openai.register(client)
```

### Gradient Agent Connection

```python
from openai import OpenAI

client = OpenAI(
    base_url=f"{agent_endpoint}/api/v1/",
    api_key=agent_access_key,
)
```

