# Implementing Qdrant for Persistent Chat History

This document outlines the thought process and implementation steps for switching the chatbot's conversation history storage from a temporary in-memory solution to a persistent one using Qdrant.

## 1. Objective

The goal is to ensure that conversations with the chatbot are not lost when the application restarts. We will achieve this by storing the chat history in our existing Qdrant database, using the `session_id` to retrieve the history for each user session.

## 2. Why Qdrant for Chat History?

While Qdrant is primarily a vector database used for document retrieval (the "RAG" part of our application), the LangChain framework provides a convenient adapter, `QdrantChatMessageHistory`, that allows it to be used as a persistent store for conversations.

This approach is efficient because it leverages our existing database infrastructure. It works by storing each chat message as a "point" (similar to a record) in a Qdrant collection. The `session_id` is stored as metadata with each point, allowing for quick retrieval of all messages belonging to a specific conversation.

## 3. Step-by-Step Implementation Plan

### Step 1: Update Dependencies (`requirements.txt`)

-   **Action:** Ensure `langchain-qdrant` is in the `requirements.txt` file.
-   **Reasoning:** The project already had this dependency, but it's a critical first check. This is the latest package for Qdrant integration with LangChain and using it resolves deprecation warnings seen in the logs.

### Step 2: Update Configuration (`src/core/config.py`)

-   **Action:**
    1.  Add a new configuration variable, `qdrant_chat_history_collection`, to the `Config` class. We'll give it a default value like `"chatbot_chat_history"`.
    2.  Change the import statement for `Qdrant` from `langchain_community.vectorstores` to `langchain_qdrant`.
-   **Reasoning:**
    1.  Defining a specific collection for chat messages keeps them cleanly separated from the document vectors used for retrieval.
    2.  Updating the import statement allows us to use the most current version of the Qdrant integration, which is good practice and silences deprecation warnings.

### Step 3: Update Chat History Logic (`src/core/chat_manager.py`)

-   **Action:**
    1.  Import `QdrantChatMessageHistory` from `langchain_community.chat_message_histories`.
    2.  Replace the existing `get_session_history` function. The new function will initialize a Qdrant client and return an instance of `QdrantChatMessageHistory`, configured with the client, the `session_id`, and the new collection name from our config.
    3.  Remove the global `store = {}` dictionary, as it is no longer needed.
-   **Reasoning:** This is the core of the change. It swaps the temporary in-memory dictionary with a robust, database-backed history object. The `QdrantChatMessageHistory` object handles all the complexities of saving to and reading from the database.

### Step 4: Retain Manual History Management (in `generate_response`)

-   **Action:** Keep the existing logic in the `generate_response` function that manually fetches the history, runs the chain, and then manually saves the new messages.
-   **Reasoning:** This is a critical and nuanced point. The chatbot's AI chain is designed to produce a "structured output" (a Pydantic object containing `category`, `answer`, etc.). Standard LangChain history tools like `RunnableWithMessageHistory` expect a simple string as the output and will fail with this structured data, which was the cause of a `ValueError` we fixed earlier.

    By continuing to manage the history manually within the `generate_response` function, we retain the benefit of the structured output while ensuring the conversation is correctly saved to Qdrant via our new `QdrantChatMessageHistory` object. It's the most reliable way to accommodate our application's specific design.
