from google.adk.agents import SequentialAgent

from .prompt import STORY_BOOK_MAKER_DESCRIPTION
from .sub_agents.illustrator.orchestrator import illustrator_orchestrator
from .sub_agents.story_writer.agent import story_writer_agent


MODEL = "openai/gpt-4o"

story_book_maker_agent = SequentialAgent(
    name="StoryBookMakerAgent",
    description=STORY_BOOK_MAKER_DESCRIPTION,
    sub_agents=[story_writer_agent, illustrator_orchestrator],
)

root_agent = story_book_maker_agent
