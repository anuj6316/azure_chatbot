from .config import get_config


def get_relevant_docs(vectorstore, query, k=None):
    """Retrieve relevant documents from vectorstore.
    
    Args:
        vectorstore: The vectorstore to search
        query: The query string
        k: Number of results to return (defaults to config.retriever_top_k)
    """
    if k is None:
        k = get_config().retriever_top_k
    return vectorstore.similarity_search(query, k=k)
