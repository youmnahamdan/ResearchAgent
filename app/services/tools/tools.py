from ast import parse
import asyncio 
import json
from typing import List
from pydantic import BaseModel
from openai import OpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .prompt_loader import prompt_loader
from utils.logger import Logger
from dotenv import load_dotenv

load_dotenv()

logger = Logger.get_logger()

# use runnableparallel
def generate_completion(messages, response_format):
    logger.debug("making OpenAI client")
    return OpenAI().beta.chat.completions.parse(
        model="gpt-5-nano",
        messages=messages,
        response_format=response_format
    )


class ResearchAnalysisResult(BaseModel):
    summary: str
    key_insights: List[str]
    follow_up_questions: List[str]



class ResearchTool:
    """Unified class for agent-compatible research tools."""

    class SummaryModel(BaseModel):
        summary: str = ""

    class InsightsModel(BaseModel):
        insights: List[str] = []

    class QuestionsModel(BaseModel):
        questions: List[str] = []

    def __init__(self):
        pass

    async def build_messages(self, system_prompt: str, user_content: str):
        return [
            SystemMessage(content=system_prompt, role="system"),
            HumanMessage(content=user_content, role="user")
        ]

    async def summarize(self, text: str) -> str:
        logger.debug(f"Summarize Research")
        messages = await self.build_messages(prompt_loader("summarize.txt"), text)
        response = generate_completion(messages, response_format=self.SummaryModel)
        return response.choices[0].message.parsed.summary

    async def extract_insights(self, text: str) -> List[str]:
        logger.debug(f"Extract Insights")
        messages = await self.build_messages(prompt_loader("provide_insights.txt"), text)
        response = generate_completion(messages, response_format=self.InsightsModel)
        return response.choices[0].message.parsed.insights

    async def generate_questions(self, text: str) -> List[str]:
        logger.debug(f"Generating Questions")
        messages = await self.build_messages(prompt_loader("generate_questions.txt"), text)
        response = generate_completion(messages, response_format=self.QuestionsModel)
        return response.choices[0].message.parsed.questions

    async def await_tools(self, text: str) -> ResearchAnalysisResult:
        summary_task = self.summarize(text)
        insights_task = self.extract_insights(text)
        questions_task = self.generate_questions(text)

        summary_text, key_insights, follow_up_questions = await asyncio.gather(
            summary_task, insights_task, questions_task
        )

        return ResearchAnalysisResult(
            summary=summary_text,
            key_insights=key_insights,
            follow_up_questions=follow_up_questions
        )
    
    def analyze_research(self, text: str) -> ResearchAnalysisResult:
        """Summarize, provide insights, and generate follow-up questions.
        Args:
            - text: research content.
        """
        try: 
            analysis_result = asyncio.run(self.await_tools(text))
            logger.debug(f"Analysis Result: {analysis_result}")
            return analysis_result
        except RuntimeError:
            logger.info(f"An even loop alreasy exists")
            return asyncio.get_event_loop().run_until_complete(self.await_tools(text))
