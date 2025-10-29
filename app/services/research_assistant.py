from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from .tools.prompt_loader import prompt_loader
from .tools.tools import ResearchTool
from app.utils.logger import Logger


class ResearchAgent:
    def __init__(self, model="gpt-5-nano", temperature=0.15):
        self.logger = Logger().get_logger()
        try:
            self.model = ChatOpenAI(model=model, temperature=temperature)
            self.memory = MemorySaver()
            self.agent = create_agent(
                system_prompt=self.__load_system_prompt(),
                model=self.model,
                tools=self.__load_tools(),
                checkpointer=self.memory,
            )
            self.logger.debug("Agent was created successfully")
        except Exception as e:
            self.logger.error(f"An error happed while creating the agent: {e}")

    def __load_system_prompt(self):
        return prompt_loader("system_prompt.txt")

    def __load_tools(self):
        tools = [ResearchTool().analyze_research]
        return tools

    def run(self, research_content: str, thread_id: str = "1"):
        config = {"configurable": {"thread_id": thread_id}}
        response = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Research content:  {research_content}",
                    }
                ]
            },
            config=config,
        )
        self.logger.debug(response)
        return response["messages"][-1].content
