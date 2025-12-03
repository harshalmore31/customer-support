"""FastAPI Customer Support Chatbot with Memori v3 - Automatic Memory"""

import csv
import json
import uuid
from typing import List

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config import (
    DEMO_DIR,
    SYSTEM_PROMPT,
    TICKETS_CSV,
    ChatRequest,
    ChatResponse,
    TicketInfo,
    get_memori_for_user,
    openai_client,
)
from tools import TOOLS, execute_tool

app = FastAPI(title="Customer Support Chatbot API - v3 Auto Memory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def chat_completion(messages, tools=None, tool_choice=None):
    """Run OpenAI call asynchronously"""
    if tools:
        return await openai_client.chat.completions.create(
            model="n/a", messages=messages, tools=tools, tool_choice=tool_choice
        )
    return await openai_client.chat.completions.create(model="n/a", messages=messages)


@app.get("/")
async def root():
    return FileResponse(DEMO_DIR / "index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, response: Response):
    response.set_cookie(
        key="memori_user_id",
        value=request.user_id,
        max_age=31536000,
        httponly=False,
        samesite="lax",
    )

    session_id = request.session_id or f"session_{uuid.uuid4().hex[:12]}"

    # Memori v3: Create fresh instance per user with their attribution
    memori = get_memori_for_user(request.user_id, session_id)
    memori.openai.register(openai_client)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request.message},
    ]

    response_obj = await chat_completion(messages, TOOLS, "auto")

    assistant_message = response_obj.choices[0].message
    ticket_created = False
    ticket_id = None

    if assistant_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in assistant_message.tool_calls
            ],
        })

        for tool_call in assistant_message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = execute_tool(tool_call.function.name, request.user_id, session_id, args)

            if tool_call.function.name == "create_support_ticket":
                ticket_created = True
                ticket_id = result.get("ticket_id")

            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
            )

        final_response = await chat_completion(messages)
        final_message = final_response.choices[0].message.content
    else:
        final_message = assistant_message.content

    return ChatResponse(
        response=final_message,
        session_id=session_id,
        ticket_created=ticket_created,
        ticket_id=ticket_id,
    )


@app.get("/api/tickets", response_model=List[TicketInfo])
async def get_tickets(user_id: str = None):
    if not TICKETS_CSV.exists():
        return []

    tickets = []
    with open(TICKETS_CSV, "r") as f:
        for row in csv.DictReader(f):
            if user_id is None or row["user_id"] == user_id:
                tickets.append(TicketInfo(**row))
    return tickets


@app.get("/api/memories/{user_id}")
async def get_user_memories(user_id: str, query: str = "customer information"):
    """Retrieve what Memori knows about a user - useful for debugging or "My Profile" feature"""
    memori = get_memori_for_user(user_id)
    facts = memori.recall(query, limit=10)
    return {
        "user_id": user_id,
        "memories": [
            {"content": f["content"], "similarity": round(f.get("similarity", 0), 3)}
            for f in facts
        ],
    }


@app.delete("/api/session/{user_id}")
async def new_session(user_id: str):
    """Start a fresh conversation session for a user"""
    memori = get_memori_for_user(user_id)
    memori.new_session()
    return {"status": "ok", "message": "New session started"}


@app.get("/api/health")
async def health():
    return {"status": "healthy", "memori_version": "v3", "mode": "auto_memory"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
