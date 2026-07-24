import langgraph 
import typing
from langgraph.graph import StateGraph,add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict,Annotated


class AgentState(TypedDict):
    """hared state passed between all nodes."""
    messages:Annotated[list[BaseMessage],add_messages]