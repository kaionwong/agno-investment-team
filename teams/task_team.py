"""
Task Team
---------

Chair autonomously decomposes complex tasks with dependencies.
Best for: multi-step portfolio construction and analysis.
"""

from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from os import getenv

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

task_team = Team(
    id="task-team",
    name="Investment Team - Task",
    mode=TeamMode.tasks,
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
        "Decompose complex investment tasks into sub-tasks with dependencies.",
        "Assign each sub-task to the most appropriate analyst.",
        "Parallelize independent tasks (e.g., fundamentals + technicals).",
        "Ensure risk assessment happens after fundamental + technical analysis.",
        "Memo writing should be the final step after all analysis is complete.",
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
