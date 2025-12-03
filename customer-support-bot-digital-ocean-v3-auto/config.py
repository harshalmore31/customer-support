"""Configuration for Memori v3 with Automatic Recall"""

import csv
import os
from pathlib import Path
from typing import Optional

from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from memori import Memori

# Load .env from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

DEMO_DIR = Path(__file__).parent
TICKETS_CSV = DEMO_DIR / "tickets.csv"


def get_database_url() -> str:
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    return "postgresql+psycopg2://postgres@localhost:5432/memoriv3_do2"


DATABASE_URL = get_database_url()


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    ticket_created: bool = False
    ticket_id: Optional[str] = None


class TicketInfo(BaseModel):
    ticket_id: str
    user_id: str
    session_id: str
    subject: str
    description: str
    priority: str
    status: str
    created_at: str


def init_openai() -> AsyncOpenAI:
    agent_endpoint = os.getenv("AGENT_ENDPOINT") or os.getenv("agent_endpoint")
    agent_access_key = os.getenv("AGENT_ACCESS_KEY") or os.getenv("agent_access_key")

    if not agent_endpoint or not agent_access_key:
        raise ValueError("AGENT_ENDPOINT and AGENT_ACCESS_KEY environment variables must be set")

    base_url = agent_endpoint if agent_endpoint.endswith("/api/v1/") else f"{agent_endpoint}/api/v1/"
    return AsyncOpenAI(base_url=base_url, api_key=agent_access_key)


def init_db_session():
    engine = create_engine(DATABASE_URL)
    return sessionmaker(bind=engine)


def init_memori_schema(db_session_factory):
    """Build database schema once at startup"""
    Memori(conn=db_session_factory).config.storage.build()


def get_memori_for_user(user_id: str, session_id: str = None) -> Memori:
    """Create a fresh Memori instance for each user request"""
    mem = Memori(conn=db_session_factory)
    mem.attribution(entity_id=user_id, process_id="support_bot")

    # Configure recall settings for customer support context
    mem.config.recall_facts_limit = 5
    mem.config.recall_relevance_threshold = 0.15
    mem.config.session_timeout_minutes = 60

    if session_id:
        mem.set_session(session_id)
    return mem


def init_tickets_csv() -> None:
    if not TICKETS_CSV.exists():
        with open(TICKETS_CSV, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "ticket_id", "user_id", "session_id", "subject",
                    "description", "priority", "status", "created_at",
                ],
            )
            writer.writeheader()


db_session_factory = init_db_session()
openai_client = init_openai()
init_memori_schema(db_session_factory)
init_tickets_csv()

SYSTEM_PROMPT = """You are a professional customer support assistant. Your role is to:

1. Answer customer questions clearly and accurately
2. Troubleshoot common issues with step-by-step guidance
3. Be empathetic, patient, and professional at all times
4. Create support tickets for complex issues that require follow-up
5. Check and provide ticket status when customers ask

Available Tools:
- create_support_ticket: Use when a customer has an issue that cannot be resolved immediately
- check_ticket_status: Use when customers ask about their ticket status

Guidelines:
- Maintain context from previous messages in the conversation
- If you remember the customer's name or previous issues, reference them naturally
- For urgent issues, set priority to "high" or "urgent"
- Always confirm ticket creation with the ticket ID
- Be concise but thorough in your responses"""
