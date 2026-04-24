from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.graph.message import add_messages


class ChatSchema(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOllama(
    model="llama3.2",
    base_url="http://localhost:11434",
    streaming=False
)

def chat_node(state: ChatSchema):
    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }

checkpointer = InMemorySaver()

graph = StateGraph(ChatSchema)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


