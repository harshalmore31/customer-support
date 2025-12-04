"""
Demo: Using DigitalOcean Gradient AI Agents with Memori
=======================================================
This example shows how to add persistent memory to your AI agent
using Memori with PostgreSQL storage.

Key Features:
- Automatic memory tracking (no manual save/recall)
- PostgreSQL persistence for conversation history
- OpenAI-compatible API with DigitalOcean Gradient
"""

import time
import os
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from memori import Memori

load_dotenv()

# =============================================================================
# Step 1: Database Setup
# =============================================================================
print("[1/4] Setting up PostgreSQL connection...")
engine = create_engine(
    "postgresql+psycopg2://postgres@localhost:5432/memori-v3"
)
db_session_factory = sessionmaker(bind=engine)
print("      Database connected successfully")



# =============================================================================
# Step 2: Load DigitalOcean Gradient Credentials
# =============================================================================
print("[2/4] Loading Gradient AI credentials...")
agent_endpoint = os.getenv("AGENT_ENDPOINT") or os.getenv("agent_endpoint")
agent_access_key = os.getenv("AGENT_ACCESS_KEY") or os.getenv("agent_access_key")

if not agent_endpoint or not agent_access_key:
    raise ValueError("AGENT_ENDPOINT and AGENT_ACCESS_KEY must be set in .env")
print("      Credentials loaded")



# =============================================================================
# Step 3: Initialize Memori Storage
# =============================================================================
print("[3/4] Initializing Memori storage tables...")
Memori(conn=db_session_factory).config.storage.build()
print("      Storage ready")



# =============================================================================
# Step 4: Connect to DigitalOcean Gradient Agent
# =============================================================================
print("[4/4] Connecting to Gradient AI Agent...")
base_url = agent_endpoint if agent_endpoint.endswith("/api/v1/") else f"{agent_endpoint}/api/v1/"
client = OpenAI(
    base_url=base_url,
    api_key=agent_access_key,
)

# Initialize Memori with user attribution for memory tracking
mem = Memori(conn=db_session_factory)
mem.attribution(entity_id="user_456", process_id="gradient_agent")

# Register Memori with the OpenAI client for automatic memory
mem.openai.register(client)
print("      Agent connected with automatic memory enabled")



# =============================================================================
# Interactive Chat Loop
# =============================================================================
print()
print("=" * 60)
print("  DigitalOcean Gradient AI Agent with Memori")
print("  Memory is automatically persisted across sessions")
print("=" * 60)
print("Commands: 'exit' to quit")
print()

while True:
    try:
        user_input = input("You: ")
        if not user_input.strip():
            continue

        if user_input.lower() in ['exit', 'quit', 'q']:
            break

        # Memori automatically handles memory - just call the API normally
        response = client.chat.completions.create(
            model="n/a",  # Model is determined by the Gradient agent
            messages=[{"role": "user", "content": user_input}]
        )

        print(f"Agent: {response.choices[0].message.content}")
        print()

    except (EOFError, KeyboardInterrupt):
        print()  # Clean line break
        break
    except Exception as e:
        print(f"Error: {e}")
        continue

print()
print("Saving conversation to memory...")
time.sleep(2)
print("Session ended. Memories persisted to PostgreSQL.")
