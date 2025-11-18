import os
from datetime import datetime
from typing import Literal, Union
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from .config import get_config, get_vectorstore
from .prompt import prompt_template
from .retriver import get_relevant_docs

load_dotenv()

# ---------------------
#  Pydantic Output Model
# ---------------------


class QueryResponse(BaseModel):
    category: Literal[
        "greeting", "document_query", "general_info", "goodbye", "chitchat"
    ] = Field(description="The classified category of the user's query")
    answer: str = Field(description="Response text")
    context_used: bool = Field(description="Whether RAG context was used")


parser = PydanticOutputParser(pydantic_object=QueryResponse)

# ---------------------
#  Chat History (Updated)
# ---------------------

from langchain_community.chat_message_histories import SQLChatMessageHistory

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Get chat history from SQLite database.
    """
    # Ensure the directory exists
    db_path = "sqlite:///data/chat_history/chat_history.db"
    os.makedirs("data/chat_history", exist_ok=True)
    
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string=db_path
    )


# ---------------------
#  LLM
# ---------------------


def get_llm(model_name=None):
    """Get LLM instance.
    
    Args:
        model_name: Name of the model to use (defaults to config.model_name)
    """
    if model_name is None:
        model_name = get_config().model_name
    return ChatGoogleGenerativeAI(model=model_name)


# ---------------------
# Generate Response
# ---------------------


def generate_response(llm, context, query, session_id: str):
    context_text = "\n".join([doc.page_content for doc in context])

    # Build prompt from string template
    chat_prompt_template = ChatPromptTemplate.from_template(prompt_template)

    # Load existing chat history
    history = get_session_history(session_id)

    # Convert history into plain text
    chat_history_str = "\n".join(
        f"{msg.type.capitalize()}: {msg.content}" for msg in history.messages
    )

    # Build chain
    chain = (
        chat_prompt_template.partial(
            format_instructions=parser.get_format_instructions()
        )
        | llm
        | parser
    )

    # Run LLM
    response: QueryResponse = chain.invoke(
        {
            "context_text": context_text,
            "query": query,
            "chat_history": chat_history_str,
        }
    )

    # Update history manually
    history.add_user_message(query)
    history.add_ai_message(response.answer)

    return response.dict()


def get_chat_history_messages(session_id: str):
    """Retrieve raw messages for a session."""
    history = get_session_history(session_id)
    return history.messages


# ---------------------
#  TEST
# ---------------------

if __name__ == "__main__":
    query = "what is the use of apple"

    llm = get_llm()
    vectorstore = get_vectorstore()
    context = get_relevant_docs(vectorstore, query)

    session_id = "test_session"

    response = generate_response(llm, context, query, session_id)

    print(f"Category: {response['category']}")
    print(f"Answer: {response['answer']}")
    print(f"Context Used: {response['context_used']}")
