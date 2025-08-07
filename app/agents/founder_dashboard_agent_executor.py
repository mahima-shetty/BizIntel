"""
Founder Dashboard Agent Executor (Structured Tool Version)
----------------------------------------------------------
Uses AgentExecutor + LLMSingleActionAgent with structured tools for:
- Fetching news
- Summarizing articles
- Getting funding updates
"""

import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import StructuredTool
from langchain_groq import ChatGroq
from typing import List
from pydantic import BaseModel, Field
from langchain.chains import LLMChain

# Load env vars
load_dotenv()

# Import your existing agent logic
from app.agents.aggregator import aggregate_news
from app.agents.summarization_agent import summarize_articles
from app.agents.funding_agent import fetch_funding_news

# -----------------------
# ✅ Define Input Schemas
# -----------------------

class NewsInput(BaseModel):
    topic: str = Field(..., description="Topic for news search")
    count: int = Field(..., description="Number of articles to fetch")
    sources: List[str] = Field(..., description="List of news sources")

class SummarizeInput(BaseModel):
    articles: List[str] = Field(..., description="List of article texts to summarize")

class FundingInput(BaseModel):
    count: int = Field(..., description="Number of funding updates to fetch")

# -----------------------
# ✅ Define Structured Tools
# -----------------------

news_tool = StructuredTool.from_function(
    func=aggregate_news,
    name="get_news",
    args_schema=NewsInput,
    description="Fetch latest market news articles based on topic and sources."
)

summary_tool = StructuredTool.from_function(
    func=summarize_articles,
    name="summarize_news",
    args_schema=SummarizeInput,
    description="Summarize a list of news articles into concise insights."
)

funding_tool = StructuredTool.from_function(
    func=fetch_funding_news,
    name="get_funding_news",
    args_schema=FundingInput,
    description="Fetch the latest funding news for startups."
)

tools = [news_tool, summary_tool, funding_tool]

# -----------------------
# ✅ LLM Setup
# -----------------------

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)



# -----------------------
# ✅ Custom Prompt
# -----------------------

prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    template="""
You are an autonomous business analyst agent. Your goal:
- Fetch latest market news (via get_news)
- Summarize news (via summarize_news)
- Fetch funding news (via get_funding_news)

Follow these steps:
{agent_scratchpad}

User query:
{input}

Respond with a concise, actionable report.
"""
)

# -----------------------
# ✅ Output Parser
# -----------------------

from langchain.agents import AgentOutputParser
import re


class CustomOutputParser(AgentOutputParser):
    def parse(self, text: str):
        if "Action:" in text:
            match = re.search(r"Action: (.*)\nAction Input: (.*)", text, re.DOTALL)
            if match:
                return AgentAction(tool=match.group(1).strip(), tool_input=eval(match.group(2).strip()), log=text)
        return AgentFinish(return_values={"output": text}, log=text)

output_parser = CustomOutputParser()

# -----------------------
# ✅ Agent + Executor
# -----------------------
llm_chain = LLMChain(
    prompt=prompt,
    llm=llm
)


agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=[t.name for t in tools]
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# -----------------------
# ✅ Run Function
# -----------------------
import json

def run_founder_agent(user_prefs: dict) -> dict:
    query = f"""
    Generate a founder dashboard report in JSON format with the following structure:
    {{
        "market_news": [
            {{"title": "...", "source": "...", "summary": "...", "url": "..."}}
        ],
        "summary": "...",
        "funding_updates": [
            {{"company": "...", "amount": "...", "valuation": "...", "sector": "...", "url": "..."}}
        ],
        "insights": ["...", "...", "..."]
    }}

    Rules:
    - Respond ONLY with valid JSON, no extra text.
    - Ensure each news item includes a valid clickable URL (realistic link, can be placeholder if unavailable).
    - Summaries should be 1-2 sentences, clear and concise.
    - Do not escape JSON or wrap it in markdown.
    User preferences:
    Topic: {user_prefs.get('topic', 'Startups')}
    Sources: {', '.join(user_prefs.get('sources', []))}
    Funding Count: {user_prefs.get('funding_count', 5)}
    """

    result = agent_executor.invoke({"input": query, "agent_scratchpad": ""})
    
    try:
        return json.loads(result["output"])
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from agent"}