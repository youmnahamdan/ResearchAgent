'''

# use async funcs and  / batch calls
input {
reserch content  / file
question/query
}

output {
summary
key - insights
These are the core takeaways or discoveries extracted from the given text.
They capture what’s new, important, or surprising — like the “Aha!” moments a human reader would note down.

follow-up questions
These are deep, reflective, or research-oriented questions that arise naturally after reading the text.
They invite further exploration — just like a curious researcher or reviewer would ask.
}


tools:
* summarize research content
* extract key insights
* generate follow up questions

each tool will have a prompt and will run async
'''


from urllib import response
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from .tools.prompt_loader import prompt_loader 
from .tools.tools import ResearchTool
from utils.logger import Logger



class ResearchAgent():
    def __init__(self, model="gpt-5-nano", temperature=0.15):
        self.logger = Logger.get_logger()
        try:
            self.model = ChatOpenAI(model=model, temperature=temperature)
            self.memory = MemorySaver()
            self.agent = create_agent(
                system_prompt=self.__load_system_prompt(),
                model=self.model,
                tools=self.__load_tools(),
                checkpointer=self.memory
            )
            self.logger("Agent was created successfully")
        except Exception as e:
            self.logger.error(f"An error happed while creating the agent: {e}")

    def __load_system_prompt(self):
        return prompt_loader("system_prompt.txt")

    def __load_tools(self):
        tools = [
            ResearchTool().analyze_research
        ]
        return tools

    def run(self, research_content: str, thread_id: str = "1"):
        config = {"configurable": {"thread_id": thread_id}}
        response = self.agent.invoke(
            {"messages": [{"role": "user", "content": f"Research content:  {research_content}"}]},
            config=config
        )
        self.logger.debug(response)
        return response["messages"][-1].content

