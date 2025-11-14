from langchain_community.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from .config import get_config

config = get_config()


def create_qdrant_vectorstore(
    docs,
    collection_name=config.qdrant_collection,
    embedding_model_name=config.embedding_model,
    qdrant_url=config.qdrant_url,
):
    # Initialize the embedding model
    client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
    client.delete_collection(collection_name=collection_name)
    print(f"Collection '{collection_name}' deleted successfully.")

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    # Create Qdrant vectorstore and add documents
    vectorstore = Qdrant.from_documents(
        documents=docs,
        embedding=embeddings,
        url=qdrant_url,
        collection_name=collection_name,
    )
    return vectorstore
