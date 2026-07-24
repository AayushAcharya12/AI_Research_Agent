"""Confugring everything that our projects want like(llm models,api keys)"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()

tavily_api=os.getenv("TAVILY_API")
groq_api_key=os.getenv('groq_new_api')

#Lets validate our API Keys
if not tavily_api:
    print('Sorry!Tavily API key not found in .env')

if not groq_api_key:
    print('Sorry!GROQ API key now found in .env')

llm=ChatGroq(model='llama-3.1-8b-instant',groq_api_key=groq_api_key)