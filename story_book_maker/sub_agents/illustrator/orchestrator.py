from google.adk.agents import ParallelAgent

from ...constants import ILLUSTRATION_PAGE_COUNT
from .agent import make_illustrator_agent
from .progress_agent import make_progress_message_agent

illustrator_orchestrator = ParallelAgent(
    name="illustrator_orchestrator",
    description=(
        "Orchestrates page-specific illustrator agents (one JPEG per fairy-tale "
        "page 1–5) after the story writer step."
    ),
    sub_agents=[
        make_progress_message_agent(p, make_illustrator_agent(p))
        for p in range(1, ILLUSTRATION_PAGE_COUNT + 1)
    ],
)
