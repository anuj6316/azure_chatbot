import logging
import os
from langchain_community.document_loaders import (
    PyMuPDFLoader, 
    Docx2txtLoader, 
    TextLoader, 
    CSVLoader, 
    UnstructuredExcelLoader as ExcelLoader,  # Note: ExcelLoader is often UnstructuredExcelLoader
    UnstructuredMarkdownLoader, 
    DirectoryLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .logger import setup_logger

# Configure logging
logger = setup_logger(__name__)

# Configuration
KNOWLEDGE_BASE_DIR = "/home/anuj/DataScience_Rag_Model/data"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_docs(base_path=KNOWLEDGE_BASE_DIR):
    docs = []
    
    # Ensure path exists
    if not os.path.isdir(base_path):
        logger.error(f"Knowledge base directory does not exist: {base_path}")
        return docs

    loaders_config = [
        ("PDF", "**/*.pdf", PyMuPDFLoader),
        ("DOCX", "**/*.docx", Docx2txtLoader),
        ("TXT", "**/*.txt", TextLoader),
        ("CSV", "**/*.csv", CSVLoader),
        ("XLSX", "**/*.xlsx", ExcelLoader),
        ("Markdown", "**/*.md", UnstructuredMarkdownLoader),
    ]

    for file_type, glob_pattern, loader_cls in loaders_config:
        logger.info(f"🔍 Loading {file_type} files from {base_path} with pattern '{glob_pattern}'...")
        try:
            loader = DirectoryLoader(
                path=base_path,
                glob=glob_pattern,
                loader_cls=loader_cls,
                show_progress=True,
                use_multithreading=True,  # optional: speeds up I/O-bound loading
                max_concurrency=4          # optional
            )
            loaded_docs = loader.load()
            docs.extend(loaded_docs)
            logger.info(f"✅ Loaded {len(loaded_docs)} {file_type} documents. Total so far: {len(docs)}")
        except Exception as e:
            logger.error(f"❌ Failed to load {file_type} files: {e}", exc_info=True)

    logger.info(f"📄 Total documents loaded: {len(docs)}")
    return docs


def split_docs(docs, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    logger.info(f"✂️ Starting document splitting: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )
        chunks = text_splitter.split_documents(docs)
        logger.info(f"✅ Split into {len(chunks)} text chunks")
        return chunks
    except Exception as e:
        logger.error(f"❌ Error during document splitting: {e}", exc_info=True)
        return []


if __name__ == '__main__':
    try:
        logger.info("🚀 Starting data ingestion pipeline...")
        docs = load_docs()
        if not docs:
            logger.warning("⚠️ No documents were loaded. Check directory and file formats.")
        else:
            chunks = split_docs(docs)
            logger.info(f"🎉 Data ingestion completed successfully. {len(chunks)} chunks ready for embedding.")
    except Exception as e:
        logger.critical(f"💥 Critical error in main execution: {e}", exc_info=True)


def format_docs(docs):
    formatted = []
    for doc in docs:
        formatted.append({
            "text": doc.page_content.strip(),  # For reranker + LLM
            "meta": {
                "title": doc.metadata.get("title"),
                "page": doc.metadata.get("page"),
                "source": doc.metadata.get("source"),
                "file_path": doc.metadata.get("file_path"),
                "_id": doc.metadata.get("_id"),
                "collection": doc.metadata.get("_collection_name")
            }
        })
    return formatted

def get_reranked_with_metadata(reranked_texts, all_chunks):
    results = []

    for text in reranked_texts:
        for chunk in all_chunks:
            if chunk["text"] == text:
                results.append(chunk)
                break
    return results
