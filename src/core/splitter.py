from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from .config import get_config

config = get_config()


def split_documents(
    documents, chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)
