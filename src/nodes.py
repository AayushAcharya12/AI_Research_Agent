#Making nodes for our chatbot
from config import llm
from states import AgentState
from prompts import SYSTEM_PROMPT
from langchain.messages import SystemMessage
from tools import search_tool
#making chatbot node
def chatbot(state:AgentState):
    """Main chatbot node.

    Reads the conversation history,
    sends it to the LLM,
    and returns the AI response."""
    messages=state['messages']
    messages=messages+[SystemMessage(content=SYSTEM_PROMPT),
                      *state['messages']]
    
    #Call llm
    llm_with_tool=llm.bind_tools([search_tool])
    output=llm_with_tool.invoke(messages)
    
    return{
        "messages":[output]
    }