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
config = get_config()

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

from collections import defaultdict
from typing import List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage


class InMemoryChatMessageHistory(BaseChatMessageHistory):
    """In-memory implementation of chat message history."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages_by_session = defaultdict(list)

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the messages for the current session."""
        return self.messages_by_session[self.session_id]

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the session history."""
        self.messages_by_session[self.session_id].append(message)

    def clear(self) -> None:
        """Clear session history."""
        self.messages_by_session[self.session_id].clear()


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    return InMemoryChatMessageHistory(session_id)


# ---------------------
#  LLM
# ---------------------


def get_llm(model_name=config.model_name):
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash")


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
