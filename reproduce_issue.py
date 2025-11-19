
import os
from unittest.mock import patch
from langchain_core.documents import Document
from langchain_community.chat_message_histories import ChatMessageHistory
from src.core.chat_manager import generate_response, get_llm

# Mock context
context = [
    Document(page_content="The system architecture consists of a Client, a Load Balancer, and three Servers (Server A, Server B, Server C). The Client sends requests to the Load Balancer, which distributes them to the Servers.")
]

query = "Draw a diagram of the system architecture."
session_id = "test_session_mermaid"

llm = get_llm()

# Mock history to avoid DB issues
mock_history = ChatMessageHistory()

with patch("src.core.chat_manager.get_session_history", return_value=mock_history):
    print(f"Query: {query}")
    response = generate_response(llm, context, query, session_id)

    print("\nResponse:")
    print(f"Category: {response['category']}")
    print(f"Answer: {response['answer']}")
    print(f"Diagram (DOT): {response['diagram']}")
    
    if "digraph" in response['diagram'] or "graph" in response['diagram']:
        print("SUCCESS: Graphviz DOT code detected.")
    else:
        print("FAILURE: Graphviz DOT code NOT detected.")
