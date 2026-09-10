from langgraph.graph import StateGraph, START ,END
from app.agent.states import AgentState
from app.agent import nodes as n

# Build the agent graph
builder = StateGraph(AgentState)
builder.add_node("call_llm",n.call_llm)
builder.add_node("tool_node",n.tool_node)
builder.add_edge(START,"call_llm")
builder.add_conditional_edges("call_llm",n.route_tool_node,{"tool_node":"tool_node" , "END" : END})
builder.add_edge("tool_node","call_llm")

agent = builder.compile()