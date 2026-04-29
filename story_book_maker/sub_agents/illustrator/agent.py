from google.adk.agents import Agent

from ...constants import ILLUSTRATOR_RESULT_KEY, STORY_WRITER_RESULT_KEY
from .generate_images import generate_images

MODEL = "openai/gpt-4o"

ILLUSTRATOR_INSTRUCTION = """You are the illustration step after the story writer.

## Role
- Session state already holds the structured fairy tale under `story_writer_result` (five pages, each with `visual` scene briefs).
- Your job is to drive image generation for **every page**, using those briefs, not rewriting the story.

## What to do
1. Call the `generate_images` tool **once**. It reads `story_writer_result` from state and generates one JPEG per page in page order (matching each page's `visual` prompt).
2. Do not substitute your own prompts; the tool uses the writer's `visual` fields from state.
3. If the tool errors because state is missing or invalid, summarize the error for the user."""

illustrator_agent = Agent(
    name="illustrator_agent",
    description=(
        "Runs after the story writer: reads session state "
        f"`{STORY_WRITER_RESULT_KEY}` (five pages with `visual` briefs) and generates "
        "one illustration image per page via `generate_images`."
    ),
    instruction=ILLUSTRATOR_INSTRUCTION,
    tools=[generate_images],
    model=MODEL,
    output_key=ILLUSTRATOR_RESULT_KEY,
)
