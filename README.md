# DigitalOcean Gradient AI Agent with Persistent Memory

A demonstration of integrating DigitalOcean Gradient AI Agents with [Memori](https://github.com/MemoriLabs/Memori) for persistent conversation memory using PostgreSQL storage.

## Overview

This project showcases how to build AI-powered customer support agents using DigitalOcean's Gradient AI platform with automatic memory persistence. The integration enables:

- **Automatic Memory Tracking**: Conversations are persisted without manual save/recall operations
- **PostgreSQL Persistence**: Durable storage for conversation history across sessions
- **OpenAI-Compatible API**: Seamless integration with DigitalOcean Gradient endpoints

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

**Attribution Model:**
- **Entity**: The user interacting with the system
- **Process**: The Gradient AI agent handling requests
- **Session**: Groups related interactions for context

**Advanced Augmentation** extracts facts, preferences, and relationships asynchronously with zero latency impact.

## Prerequisites

- Python 3.10+
- PostgreSQL database
- DigitalOcean Gradient AI Agent credentials

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

## License

MIT License
