from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types


STORY_WRITER_PROGRESS_MESSAGE = "스토리 작성 중..."


class StoryWriterProgressMessageAgent(BaseAgent):
    """Emits a chat progress message, then delegates to the story writer agent."""

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            content=types.Content(
                role="model",
                parts=[types.Part(text=STORY_WRITER_PROGRESS_MESSAGE)],
            ),
        )

        async for event in self.sub_agents[0].run_async(ctx):
            yield event


def make_story_writer_progress_message_agent(child_agent: BaseAgent) -> BaseAgent:
    return StoryWriterProgressMessageAgent(
        name="story_writer_progress",
        description="Announces story writing progress, then runs the story writer agent.",
        sub_agents=[child_agent],
    )
