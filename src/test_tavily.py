from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os

load_dotenv()

api_key=os.getenv("TAVILY_API")

tool = TavilySearch(max_results=2,tavily_api_key=api_key)

result = tool.invoke({"query": "Who is the current Prime Minister of Nepal?"})

print(result)