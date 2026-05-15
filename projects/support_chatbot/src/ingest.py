import os
import argparse
import shutil
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import DATA_DIR, CHROMA_DB_DIR, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP

def ingest_data(reindex=False):
    """
    Load data, chunk it, and store in ChromaDB.
    """
    if reindex:
        print(f"Re-indexing requested. Deleting existing database at {CHROMA_DB_DIR}...")
        if os.path.exists(CHROMA_DB_DIR):
            shutil.rmtree(CHROMA_DB_DIR)
        print("Existing database deleted.")
    
    print(f"Loading documents from directory {DATA_DIR}...")
    
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory not found at {DATA_DIR}")
        return
        
    loader = DirectoryLoader(
        DATA_DIR,
        glob="**/*.md",
        loader_cls=TextLoader
    )
    documents = loader.load()
    
    if not documents:
        print(f"Warning: No markdown files found in {DATA_DIR}")
        return
    
    print(f"Splitting documents (chunk size: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Generated {len(chunks)} chunks.")
    
    print("Initializing embeddings and VectorStore...")
    embeddings = OpenAIEmbeddings()
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR
    )
    
    print("Ingestion complete. Data is persisted to ChromaDB locally.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest knowledge base into ChromaDB.")
    parser.add_argument("--reindex", action="store_true", help="Delete existing index and re-index from scratch.")
    args = parser.parse_args()
    
    ingest_data(reindex=args.reindex)
