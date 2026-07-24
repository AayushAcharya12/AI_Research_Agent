from langgraph.graph import START,END,StateGraph
from langgraph.prebuilt import tools_condition,ToolNode

from states import AgentState
from nodes import chatbot
from tools import search_tool

graph=StateGraph(AgentState)

#Adding nodes
graph.add_node("chatbot",chatbot)
graph.add_node("tools",ToolNode([search_tool]))

#adding edges
graph.add_edge(START,"chatbot")

#Add conditional edges
graph.add_conditional_edges("chatbot",tools_condition)

graph.add_edge('tools','chatbot')
graph.add_edge("chatbot",END)

graph=graph.compile()