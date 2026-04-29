import json

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from pydantic import BaseModel, Field

from constants import ILLUSTRATOR_RESULT_KEY, STORY_WRITER_RESULT_KEY


_ILLUSTRATOR_PREFIX = (
    f"You are the **Illustrator** agent. You run **after** the story writer.\n\n"
    "The story data below was read from **session state** under the key produced by the story writer "
    f"(`{STORY_WRITER_RESULT_KEY}`). It is a JSON object with a `pages` array; each item has "
    "`page_number`, `text`, and `visual_description`.\n\n"
    "## Your task\n"
    "1. Your structured output **must define exactly five images**—one illustration per page, for `page_number` 1 through 5. Do not return fewer than five or more than five image entries.\n"
    "2. For **each** of those five entries, produce an **image_prompt** that an image-generation API can use to render that spread. Ground the scene in `visual_description`; you may use `text` only for extra context, not to paste the story into the prompt.\n"
    "3. Write a **style_bible** so characters, palette, and art style stay consistent across all five prompts (children's book illustration, readable at a glance).\n"
    "4. Use **negative_prompt** per page only when useful (e.g. no scary imagery, no overlaid text).\n\n"
    "Do not invent new story beats; only illustrate what the state describes."
)


async def _illustrator_instruction(readonly_context: ReadonlyContext) -> str:
    """Build instruction with pretty-printed story state (InstructionProvider bypasses `{key}` injection)."""
    tale = readonly_context.state.get(STORY_WRITER_RESULT_KEY)
    if tale is None:
        raise KeyError(
            f"Missing `{STORY_WRITER_RESULT_KEY}` in session state; run `story_writer_agent` first.",
        )
    blob = json.dumps(tale, ensure_ascii=False, indent=2)
    return (
        _ILLUSTRATOR_PREFIX
        + "\n\n## Story state from session (JSON)\n```json\n"
        + blob
        + "\n```"
    )


illustrator_agent = Agent(
    name="illustrator_agent",
    description=(
        "Runs after the story writer: reads structured fairy tale state from "
        f"`{STORY_WRITER_RESULT_KEY}` and emits specifications for exactly five illustrations "
        "(one per page) plus a shared style bible."
    ),
    instruction=_illustrator_instruction,
    tools=[],
    model="gpt-4o-mini",
    output_key=ILLUSTRATOR_RESULT_KEY,
)
