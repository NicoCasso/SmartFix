import random
from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

# CTRL + SHIFT + P to show this 
# with LangGraph Visualizer for VSCode
# search for LangGraphV : Open with LangGraph Visualizer

class State(TypedDict):
    graph_state: str

def node_1(state: State):
    print("---Node 1---")
    return {"graph_state": state['graph_state'] +" I am"}

def node_2(state: State):
    print("---Node 2---")
    return {"graph_state": state['graph_state'] +" happy!"}

def node_3(state: State):
    print("---Node 3---")
    return {"graph_state": state['graph_state'] +" sad!"}

def decide_mood(state: State) -> Literal["node_2", "node_3"]:
    if random.random() < 0.5:
        # 50% of the time, we return Node 2
        return "node_2"
    else :
        # 50% of the time, we return Node 3
        return "node_3"

graph_builder = StateGraph(State)

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("node_1", node_1)
graph_builder.add_node("node_2", node_2)
graph_builder.add_node("node_3", node_3)

# Logic
graph_builder.add_edge(START, "node_1")
graph_builder.add_conditional_edges("node_1", decide_mood)
graph_builder.add_edge("node_2", END)
graph_builder.add_edge("node_3", END)

graph = graph_builder.compile()
