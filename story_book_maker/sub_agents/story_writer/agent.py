from google.adk.agents import Agent
from pydantic import BaseModel, Field

from ...constants import STORY_WRITER_RESULT_KEY


class ChildFairyTalePage(BaseModel):
    """One spread of the story: readable text plus art direction."""

    page_number: int = Field(
        ge=1,
        le=5,
        description="Page index from 1 to 5, in reading order.",
    )
    text: str = Field(
        description=(
            "Story text for this page: short, clear sentences for young children; "
            "warm, age-appropriate tone."
        ),
    )
    visual: str = Field(
        description=(
            "Scene brief for illustration or image generation: setting, characters, "
            "action, key props, lighting and mood; concrete and visual, not the story prose."
        ),
    )


class ChildFairyTale(BaseModel):
    """Theme-driven children's fairy tale as exactly five structured pages."""

    pages: list[ChildFairyTalePage] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="Exactly five pages: narrative arc from beginning to end.",
    )


STORY_WRITER_INSTRUCTION = """You are a children's fairy tale author.

The user's message supplies a **theme** (the core idea or topic). Build an **original** fairy tale around that theme.

## Output requirements
- Produce **exactly five pages**. Each page is one numbered unit in chronological order (page_number 1 through 5).
- **text**: prose for that page only; readable aloud, suited to young readers, with a coherent plot across all five pages (setup -> development -> climax -> resolution).
- **visual**: a self-contained illustration brief for that page (who, where, what happens, mood). Do not repeat the full story text here; describe what should be *shown*.

Stay consistent with characters and setting unless the story logic requires a change."""

MODEL = "openai/gpt-4o"

story_writer_agent = Agent(
    name="story_writer_agent",
    description=(
        "Given a theme, writes a five-page children's fairy tale as structured data: "
        "per-page narrative text plus visual scene brief (`visual`) for each page."
    ),
    instruction=STORY_WRITER_INSTRUCTION,
    tools=[],
    model=MODEL,
    output_schema=ChildFairyTale,
    output_key=STORY_WRITER_RESULT_KEY,
)
