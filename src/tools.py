#Using only tavily search tool now.
from langchain_tavily import TavilySearch
from config import tavily_api

search_tool = TavilySearch(
    max_results=5,
    topic="news",
    tavily_api_key=tavily_api
)