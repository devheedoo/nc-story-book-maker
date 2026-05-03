import json
from io import BytesIO
from typing import Any

from google.adk.tools.tool_context import ToolContext
from google.genai import types
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

from ...constants import (
    FINAL_STORY_BOOK_PDF_FILENAME,
    ILLUSTRATION_PAGE_COUNT,
    STORY_WRITER_RESULT_KEY,
    illustrator_page_result_key,
)

PAGE_WIDTH = 1024
PAGE_HEIGHT = 1536
TITLE_FONT = "HYGothic-Medium"
FALLBACK_TITLE_FONT = "Helvetica-Bold"


def _coerce_mapping(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _require_story_writer_result(tool_context: ToolContext) -> None:
    if tool_context.state.get(STORY_WRITER_RESULT_KEY) is None:
        raise ValueError(
            f"Missing `{STORY_WRITER_RESULT_KEY}` in state; cannot generate PDF."
        )


def _illustration_filename(tool_context: ToolContext, page_number: int) -> str:
    result_key = illustrator_page_result_key(page_number)
    raw_result = tool_context.state.get(result_key)
    result = _coerce_mapping(raw_result)
    if result is None:
        raise ValueError(
            f"Missing or invalid `{result_key}` in state; expected a structured "
            f"illustration result, got {type(raw_result).__name__}."
        )
    if result.get("success") is False:
        raise ValueError(
            f"`{result_key}` did not succeed: "
            f"{result.get('error_code') or result.get('message') or 'unknown error'}"
        )

    filename = result.get("filename")
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError(f"`{result_key}` does not include a valid `filename`.")
    return filename


def _inline_data_bytes(part: types.Part, filename: str) -> bytes:
    inline_data = getattr(part, "inline_data", None)
    if inline_data is None or inline_data.data is None:
        raise ValueError(f"Artifact `{filename}` does not contain inline data.")
    return bytes(inline_data.data)


def _register_title_font() -> str:
    try:
        pdfmetrics.registerFont(UnicodeCIDFont(TITLE_FONT))
        return TITLE_FONT
    except Exception:
        return FALLBACK_TITLE_FONT


def _draw_centered_title(pdf: canvas.Canvas, title: str) -> None:
    font_name = _register_title_font()
    font_size = 64
    pdf.setFont(font_name, font_size)
    pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + font_size, title.strip())


def _draw_full_page_image(pdf: canvas.Canvas, image_bytes: bytes) -> None:
    image = ImageReader(BytesIO(image_bytes))
    image_width, image_height = image.getSize()
    scale = min(PAGE_WIDTH / image_width, PAGE_HEIGHT / image_height)
    draw_width = image_width * scale
    draw_height = image_height * scale
    x = (PAGE_WIDTH - draw_width) / 2
    y = (PAGE_HEIGHT - draw_height) / 2
    pdf.drawImage(
        image,
        x,
        y,
        width=draw_width,
        height=draw_height,
        preserveAspectRatio=True,
        anchor="c",
    )


async def generate_story_book_pdf(title: str, tool_context: ToolContext):
    """Create a six-page PDF artifact from the story title and five page images."""

    title = (title or "").strip()
    if not title:
        raise ValueError("`title` must be a non-empty string.")

    _require_story_writer_result(tool_context)

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    _draw_centered_title(pdf, title)
    pdf.showPage()

    for page_number in range(1, ILLUSTRATION_PAGE_COUNT + 1):
        filename = _illustration_filename(tool_context, page_number)
        artifact = await tool_context.load_artifact(filename=filename)
        if artifact is None:
            raise ValueError(f"Missing image artifact `{filename}` for page {page_number}.")
        _draw_full_page_image(pdf, _inline_data_bytes(artifact, filename))
        pdf.showPage()

    pdf.save()
    pdf_bytes = pdf_buffer.getvalue()

    artifact = types.Part(
        inline_data=types.Blob(
            mime_type="application/pdf",
            data=pdf_bytes,
        )
    )
    await tool_context.save_artifact(
        filename=FINAL_STORY_BOOK_PDF_FILENAME,
        artifact=artifact,
    )

    print(f"Generated PDF {FINAL_STORY_BOOK_PDF_FILENAME}")

    return {
        "filename": FINAL_STORY_BOOK_PDF_FILENAME,
        "title": title,
        "page_count": ILLUSTRATION_PAGE_COUNT + 1,
        "success": True,
    }
