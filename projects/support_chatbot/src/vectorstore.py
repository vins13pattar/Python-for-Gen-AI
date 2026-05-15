import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import CHROMA_DB_DIR, COLLECTION_NAME

def get_retriever():
    """
    Returns a Chroma vector store retriever configured to return top 4 results.
    """
    if not os.path.exists(CHROMA_DB_DIR):
        print(f"Warning: Chroma DB directory not found at {CHROMA_DB_DIR}. Please run ingestion first.")
        return None
        
    embeddings = OpenAIEmbeddings()
    
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": 4})
