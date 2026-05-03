from google.adk.agents import ParallelAgent

from .agent import make_illustrator_agent

PAGE_COUNT = 5

illustrator_orchestrator = ParallelAgent(
    name="illustrator_orchestrator",
    description=(
        "Orchestrates page-specific illustrator agents (one JPEG per fairy-tale "
        "page 1–5) after the story writer step."
    ),
    sub_agents=[make_illustrator_agent(p) for p in range(1, PAGE_COUNT + 1)],
)
