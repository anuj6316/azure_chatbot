from .config import get_config

config = get_config()


def get_relevant_docs(vectorstore, query, k=config.retriever_top_k):
    return vectorstore.similarity_search(query, k=k)
