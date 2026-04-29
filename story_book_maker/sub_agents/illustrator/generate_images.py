import base64

from google.adk.tools.tool_context import ToolContext
from google.genai import types
from openai import OpenAI

from ...constants import STORY_WRITER_RESULT_KEY


def _page_sort_key(page):
    if isinstance(page, dict):
        return page.get("page_number", 0)
    return getattr(page, "page_number", 0)


def _page_visual(page) -> str:
    if isinstance(page, dict):
        return page.get("visual") or ""
    return getattr(page, "visual", "") or ""


def _visual_prompts_from_state(story_writer_result) -> list[str]:
    """Build ordered image prompts from Story Writer output."""
    if story_writer_result is None:
        return []

    if isinstance(story_writer_result, dict):
        pages = story_writer_result.get("pages") or []
    else:
        pages = getattr(story_writer_result, "pages", None) or []

    ordered = sorted(pages, key=_page_sort_key)
    return [_page_visual(p) for p in ordered]


async def generate_images(tool_context: ToolContext):
    """Read fairy tale pages from session state and generate one image per page."""

    story_writer_result = tool_context.state.get(STORY_WRITER_RESULT_KEY)
    optimized_prompts = _visual_prompts_from_state(story_writer_result)

    if not optimized_prompts:
        raise ValueError(
            f"Missing or empty `{STORY_WRITER_RESULT_KEY}` in state; "
            "cannot generate page images."
        )

    for i, prompt in enumerate(optimized_prompts):
        if not str(prompt).strip():
            raise ValueError(
                f"`story_writer_result` page index {i} has empty `visual`."
            )

    client = OpenAI()
    filenames: list[str] = []

    for index, visual in enumerate(optimized_prompts, start=1):
        filename = f"visual_{index}.jpeg"

        image = client.images.generate(
            model="gpt-image-1",
            prompt=visual,
            n=1,
            quality="low",
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1536",
        )

        image_bytes = base64.b64decode(image.data[0].b64_json)

        artifact = types.Part(
            inline_data=types.Blob(
                mime_type="image/jpeg",
                data=image_bytes,
            )
        )

        await tool_context.save_artifact(
            filename=filename,
            artifact=artifact,
        )

        filenames.append(filename)
        print(f"Generated image {filename}")

    return {
        "image_count": len(filenames),
        "filenames": filenames,
    }
