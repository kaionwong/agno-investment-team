"""
Agentic Investment Team
-----------------------------

A multi-agent investment team demonstrating 5 architectures.

Run:
    python -m app.main
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import os
from pathlib import Path

# Monkey-patch openai.types.chat to handle missing ChatCompletionAudio in older openai versions
import sys
try:
    from openai.types.chat import ChatCompletionAudio
except ImportError:
    # ChatCompletionAudio doesn't exist in openai <1.40, create a dummy
    class ChatCompletionAudio:
        pass
    import openai.types.chat
    openai.types.chat.ChatCompletionAudio = ChatCompletionAudio
    sys.modules['openai.types.chat'].ChatCompletionAudio = ChatCompletionAudio

from agno.os import AgentOS

from agents import (
    committee_chair,
    financial_analyst,
    knowledge_agent,
    market_analyst,
    memo_writer,
    risk_officer,
    technical_analyst,
)
from db import get_postgres_db
from teams import broadcast_team, coordinate_team, route_team, task_team
from workflows import investment_workflow

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Agentic Investment Team",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[
        market_analyst,
        financial_analyst,
        technical_analyst,
        risk_officer,
        knowledge_agent,
        memo_writer,
        committee_chair,
    ],
    teams=[coordinate_team, route_team, broadcast_team, task_team],
    workflows=[investment_workflow],
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RUNTIME_ENV", "") == "dev"
    agent_os.serve(app="app.main:app", port=port, reload=reload)
