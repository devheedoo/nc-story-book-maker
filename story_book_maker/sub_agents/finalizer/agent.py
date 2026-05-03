import json

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext

from ...constants import (
    FINAL_STORY_BOOK_RESULT_KEY,
    ILLUSTRATION_PAGE_COUNT,
    STORY_WRITER_RESULT_KEY,
    illustrator_page_result_key,
)
from .generate_pdf import generate_story_book_pdf

MODEL = "openai/gpt-4o"

_FINALIZER_PREFIX = """You are the final story book publishing step.

## Role
- Session state already holds the structured fairy tale under `story_writer_result`.
- Session state also holds one machine-readable illustrator result per page, under
  `illustrator_result_page_1` through `illustrator_result_page_5`.
- Your job is to create the final six-page PDF artifact.

## What to do
1. Generate one short, child-friendly title from the story in `story_writer_result`.
2. Call the `generate_story_book_pdf` tool exactly once with that title.
3. Do not rewrite the story and do not regenerate images.
4. If the tool raises because state or artifacts are missing, summarize that error for the user.
5. Do not infer image filenames from prose; the PDF tool reads only structured illustrator results."""


async def _finalizer_instruction(readonly_context: ReadonlyContext) -> str:
    story = readonly_context.state.get(STORY_WRITER_RESULT_KEY)
    if story is None:
        raise KeyError(
            f"Missing `{STORY_WRITER_RESULT_KEY}` in session state; "
            "run `story_writer_agent` first."
        )

    story_blob = json.dumps(story, ensure_ascii=False, indent=2)
    result_keys = [
        illustrator_page_result_key(page_number)
        for page_number in range(1, ILLUSTRATION_PAGE_COUNT + 1)
    ]
    return (
        _FINALIZER_PREFIX
        + "\n\n## Required illustrator result keys\n"
        + "\n".join(f"- `{key}`" for key in result_keys)
        + "\n\n## Story state from session (JSON)\n```json\n"
        + story_blob
        + "\n```"
    )


finalizer_agent = Agent(
    name="finalizer_agent",
    description=(
        "Runs after all illustrator agents: creates a title from the story and "
        "publishes a six-page PDF artifact with one title page and five image pages."
    ),
    instruction=_finalizer_instruction,
    tools=[generate_story_book_pdf],
    model=MODEL,
    output_key=FINAL_STORY_BOOK_RESULT_KEY,
)
