"""OpenAI Tool Functions"""

import csv
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from config import TICKETS_CSV

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a support ticket for issues requiring follow-up",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                },
                "required": ["subject", "description", "priority"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_ticket_status",
            "description": "Check ticket status",
            "parameters": {
                "type": "object",
                "properties": {"ticket_id": {"type": "string"}},
                "required": [],
            },
        },
    },
]


def create_support_ticket(
    user_id: str, session_id: str, subject: str, description: str, priority: str
) -> Dict[str, Any]:
    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    ticket_data = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "session_id": session_id,
        "subject": subject,
        "description": description,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat(),
    }

    with open(TICKETS_CSV, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=ticket_data.keys()).writerow(ticket_data)

    return {
        "success": True,
        "ticket_id": ticket_id,
        "message": f"Ticket {ticket_id} created successfully.",
    }


def check_ticket_status(user_id: str, ticket_id: Optional[str] = None) -> Dict[str, Any]:
    if not TICKETS_CSV.exists():
        return {"success": False, "message": "No tickets found."}

    tickets = []
    with open(TICKETS_CSV, "r") as f:
        for row in csv.DictReader(f):
            if ticket_id:
                if row["ticket_id"] == ticket_id and row["user_id"] == user_id:
                    return {
                        "success": True,
                        "ticket": row,
                        "message": f"Ticket {ticket_id} - Status: {row['status']}, Priority: {row['priority']}",
                    }
            elif row["user_id"] == user_id:
                tickets.append(row)

    if ticket_id:
        return {"success": False, "message": f"Ticket {ticket_id} not found."}

    if tickets:
        summaries = [
            f"- {t['ticket_id']}: {t['subject']} - {t['status']} ({t['priority']})"
            for t in tickets
        ]
        return {
            "success": True,
            "tickets": tickets,
            "message": f"You have {len(tickets)} ticket(s):\n" + "\n".join(summaries),
        }

    return {"success": True, "message": "You don't have any support tickets yet."}


def execute_tool(tool_name: str, user_id: str, session_id: str, args: dict) -> dict:
    if tool_name == "create_support_ticket":
        return create_support_ticket(
            user_id, session_id, args["subject"], args["description"], args["priority"]
        )
    elif tool_name == "check_ticket_status":
        return check_ticket_status(user_id, args.get("ticket_id"))
    return {"success": False, "message": f"Unknown tool: {tool_name}"}
