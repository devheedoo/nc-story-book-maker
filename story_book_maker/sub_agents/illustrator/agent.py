from google.adk.agents import Agent

from ...constants import (
    STORY_WRITER_RESULT_KEY,
    illustrator_page_result_key,
)
from .generate_images import generate_image

MODEL = "openai/gpt-4o"


def _illustrator_instruction(page_number: int) -> str:
    return f"""You are the illustration step after the story writer.

## Role
- Session state already holds the structured fairy tale under `story_writer_result` (five pages, each with `visual` scene briefs).
- Your job is to generate exactly **one** illustration JPEG for **page {page_number}** only.

## What to do
1. Call the `generate_image` tool **once** with `page_number={page_number}`. It reads `story_writer_result` from state and uses that page's `visual` brief as the image prompt.
2. Do not substitute your own prompts; the tool uses the writer's `visual` field from state for that page.
3. If the tool returns `"success": false` (for example `"error_code": "moderation_blocked"`), explain briefly that OpenAI declined that image request and omit any raw API request IDs unless the user needs support.
4. If the tool raises because state is missing or invalid, summarize that error for the user."""


def make_illustrator_agent(page_number: int) -> Agent:
    """One ADK Agent that generates artwork for exactly one story page (1–5)."""

    return Agent(
        name=f"illustrator_agent_page_{page_number}",
        description=(
            "Runs after the story writer: reads session state "
            f"`{STORY_WRITER_RESULT_KEY}` and generates exactly one illustration for "
            f"page {page_number} via `generate_image`."
        ),
        instruction=_illustrator_instruction(page_number),
        tools=[generate_image],
        model=MODEL,
        output_key=illustrator_page_result_key(page_number),
    )
