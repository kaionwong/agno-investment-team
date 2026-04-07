"""
Coordinate Team
---------------

Chair (Gemini Pro) dynamically orchestrates analysts based on the question.
Best for: open-ended investment questions.
"""

from os import getenv

from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agno.models.ollama import Ollama
from agno.team import Team, TeamMode

from agents import (
    financial_analyst,
    knowledge_agent,
    market_analyst,
    memo_writer,
    risk_officer,
    technical_analyst,
)
from agents.settings import team_learnings

ollama_base_url = getenv("OLLAMA_BASE_URL", "http://localhost:11434")

coordinate_team = Team(
    id="coordinate-team",
    name="Investment Team - Coordinate",
    mode=TeamMode.coordinate,
    model=Ollama(id="llama3.2", host=ollama_base_url),
    members=[
        market_analyst,
        financial_analyst,
        technical_analyst,
        risk_officer,
        knowledge_agent,
        memo_writer,
    ],
    instructions=[
        "You are the Committee Chair of a $10M investment team.",
        "Dynamically decide which analysts to consult based on the question.",
        "For investment evaluations: start with Financial + Market analysts, then Risk, then Memo Writer.",
        "Always consult the Risk Officer before making allocation decisions.",
        "Provide a final recommendation with a specific dollar allocation.",
        "Ensure all decisions comply with the fund mandate.",
    ],
    learning=LearningMachine(
        knowledge=team_learnings,
        learned_knowledge=LearnedKnowledgeConfig(
            mode=LearningMode.AGENTIC,
            namespace="global",
        ),
    ),
    show_members_responses=True,
    markdown=True,
)
