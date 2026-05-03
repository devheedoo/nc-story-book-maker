import base64

from google.adk.tools.tool_context import ToolContext
from google.genai import types
from openai import APIStatusError, OpenAI

from ...constants import STORY_WRITER_RESULT_KEY, illustrator_page_result_key

MIN_PAGE = 1
MAX_PAGE = 5

# Nudges the image model away from policy edges; does not guarantee approval.
_CHILD_BOOK_IMAGE_PREFIX = (
    "Age-appropriate children's picture-book illustration. Wholesome, gentle, "
    "non-violent, no sexual content. Scene to depict:\n"
)
_STORY_TEXT_PROMPT = (
    "\n\nAdd the following exact story text as readable text in a clean caption "
    "area at the bottom of the image. Keep the text legible, warm, and integrated "
    "with the children's book page layout:\n"
)


def _openai_nested_error(exc: APIStatusError) -> tuple[str | None, str | None]:
    """Parse ``code`` and ``type`` from OpenAI's ``{"error": {...}}`` body."""

    body = exc.body
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            return err.get("code"), err.get("type")
    return None, None


def _page_number(page) -> int:
    if isinstance(page, dict):
        return int(page.get("page_number") or 0)
    return int(getattr(page, "page_number", 0) or 0)


def _page_sort_key(page):
    return _page_number(page)


def _page_visual(page) -> str:
    if isinstance(page, dict):
        return page.get("visual") or ""
    return getattr(page, "visual", "") or ""


def _page_text(page) -> str:
    if isinstance(page, dict):
        return page.get("text") or ""
    return getattr(page, "text", "") or ""


def _find_page_brief(story_writer_result, page_number: int) -> tuple[int, str, str]:
    """Resolve the `visual` and `text` fields for ``page_number``."""

    if page_number < MIN_PAGE or page_number > MAX_PAGE:
        raise ValueError(
            f"`page_number` must be between {MIN_PAGE} and {MAX_PAGE}, got {page_number}."
        )

    if story_writer_result is None:
        raise ValueError(
            f"Missing `{STORY_WRITER_RESULT_KEY}` in state; cannot generate images."
        )

    if isinstance(story_writer_result, dict):
        pages = story_writer_result.get("pages") or []
    else:
        pages = getattr(story_writer_result, "pages", None) or []

    ordered = sorted(pages, key=_page_sort_key)
    for p in ordered:
        if _page_number(p) == page_number:
            visual = _page_visual(p)
            if not str(visual).strip():
                raise ValueError(
                    f"`story_writer_result` page_number {page_number} has empty `visual`."
                )
            text = _page_text(p)
            if not str(text).strip():
                raise ValueError(
                    f"`story_writer_result` page_number {page_number} has empty `text`."
                )
            return page_number, visual, text

    raise ValueError(
        f"`story_writer_result` has no page with page_number={page_number}."
    )


async def generate_image(page_number: int, tool_context: ToolContext):
    """Read one page's brief from session state and generate a single JPEG artifact."""

    story_writer_result = tool_context.state.get(STORY_WRITER_RESULT_KEY)
    pn, visual, text = _find_page_brief(story_writer_result, page_number)

    filename = f"visual_{pn}.jpeg"
    full_prompt = (
        f"{_CHILD_BOOK_IMAGE_PREFIX}{str(visual).strip()}"
        f"{_STORY_TEXT_PROMPT}{str(text).strip()}"
    )

    client = OpenAI()
    try:
        image = client.images.generate(
            model="gpt-image-1",
            prompt=full_prompt,
            n=1,
            quality="low",
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1536",
        )
    except APIStatusError as exc:
        code, err_type = _openai_nested_error(exc)
        print(
            f"OpenAI image generation failed for page {pn}: "
            f"code={code!r} type={err_type!r} message={exc.message!r}"
        )
        result = {
            "page_number": pn,
            "filename": None,
            "success": False,
            "error_code": code or "openai_api_error",
            "error_type": err_type,
            "message": exc.message,
        }
        tool_context.state[illustrator_page_result_key(pn)] = result
        return result

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

    print(f"Generated image {filename}")

    result = {
        "page_number": pn,
        "filename": filename,
        "success": True,
    }
    tool_context.state[illustrator_page_result_key(pn)] = result
    return result
