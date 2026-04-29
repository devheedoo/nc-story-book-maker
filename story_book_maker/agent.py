from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .prompt import STORY_BOOK_MAKER_DESCRIPTION, STORY_BOOK_MAKER_PROMPT
from .sub_agents.illustrator.agent import illustrator_agent
from .sub_agents.story_writer.agent import story_writer_agent


MODEL = "openai/gpt-4o"

story_book_maker_agent = Agent(
    name="StoryBookMakerAgent",
    model=MODEL,
    description=STORY_BOOK_MAKER_DESCRIPTION,
    instruction=STORY_BOOK_MAKER_PROMPT,
    tools=[
        AgentTool(agent=story_writer_agent),
        AgentTool(agent=illustrator_agent),
    ],
)

root_agent = story_book_maker_agent
