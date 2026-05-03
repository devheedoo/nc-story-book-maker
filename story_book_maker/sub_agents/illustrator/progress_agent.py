from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from ...constants import ILLUSTRATION_PAGE_COUNT


class ProgressMessageAgent(BaseAgent):
    """Emits a chat progress message, then delegates to its single child agent."""

    page_number: int

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        message = f"이미지 {self.page_number}/{ILLUSTRATION_PAGE_COUNT} 생성 진행 중"

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(
                role="model",
                parts=[types.Part(text=message)],
            ),
        )

        async for event in self.sub_agents[0].run_async(ctx):
            yield event


def make_progress_message_agent(page_number: int, child_agent: BaseAgent) -> BaseAgent:
    return ProgressMessageAgent(
        name=f"illustrator_progress_page_{page_number}",
        description=(
            f"Announces image generation progress for page {page_number}, then "
            "runs the page illustrator agent."
        ),
        page_number=page_number,
        sub_agents=[child_agent],
    )
