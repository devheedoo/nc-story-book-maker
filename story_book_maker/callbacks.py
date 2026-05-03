"""Google ADK callbacks for user-visible progress hints (session ``state_delta``)."""

from __future__ import annotations

from google.adk.agents.callback_context import CallbackContext

from .constants import (
    ILLUSTRATION_PAGE_COUNT,
    PROGRESS_CURRENT_KEY,
    PROGRESS_MESSAGE_KEY,
    PROGRESS_PHASE_KEY,
    PROGRESS_TOTAL_KEY,
)


def _set_progress(
    state,
    *,
    phase: str,
    message: str,
    current: int | None = None,
    total: int | None = None,
) -> None:
    """Write progress fields into ADK state so they appear in ``state_delta``."""

    state[PROGRESS_PHASE_KEY] = phase
    state[PROGRESS_MESSAGE_KEY] = message
    if current is not None:
        state[PROGRESS_CURRENT_KEY] = current
    if total is not None:
        state[PROGRESS_TOTAL_KEY] = total


def show_story_writer_progress(callback_context: CallbackContext):
    """``before_agent_callback`` for ``story_writer_agent``: signal writing phase."""

    _set_progress(
        callback_context.state,
        phase="story_writer",
        message="스토리 작성 중...",
    )
    return None


def make_show_illustration_progress_before_agent(page_number: int):
    """``before_agent_callback`` for each page illustrator."""

    def before_agent_callback(
        callback_context: CallbackContext,
    ):
        msg = f"이미지 {page_number}/{ILLUSTRATION_PAGE_COUNT} 생성 진행 중"
        _set_progress(
            callback_context.state,
            phase="illustrator",
            message=msg,
            current=page_number,
            total=ILLUSTRATION_PAGE_COUNT,
        )
        return None

    return before_agent_callback
