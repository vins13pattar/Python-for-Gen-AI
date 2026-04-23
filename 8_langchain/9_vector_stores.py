"""
8. Vector Stores — Index embeddings for fast semantic search
Based on LangChain v0.3 Components Guide

Popular backends:
- FAISS — in-memory, local (no server)
- Chroma — persistent, open-source (used in this example)
- Pinecone — managed cloud
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Sample documents
docs = [
    Document(page_content="LCEL is LangChain Expression Language. Use pipe | to compose.", metadata={"source": "lcel"}),
    Document(page_content="RAG combines retrieval with generation for better answers.", metadata={"source": "rag"}),
    Document(page_content="Embeddings convert text to vectors for similarity search.", metadata={"source": "emb"}),
    Document(page_content="Chroma is a vector store for semantic search.", metadata={"source": "chroma"}),
    Document(page_content="FAISS is a vector store for semantic search.", metadata={"source": "faiss"}),
    Document(page_content="OpenAI is a company that provides AI services.", metadata={"source": "openai"}),
    Document(page_content="Google is a company that provides AI services.", metadata={"source": "google"}),
    Document(page_content="Microsoft is a company that provides AI services.", metadata={"source": "microsoft"}),
    Document(page_content="Amazon is a company that provides AI services.", metadata={"source": "amazon"}),
    Document(page_content="Meta is a company that provides AI services.", metadata={"source": "meta"}),
    Document(page_content="Apple is a company that provides AI services.", metadata={"source": "apple"}),
    Document(page_content="Samsung is a company that provides AI services.", metadata={"source": "samsung"}),
]

try:
    from langchain_chroma import Chroma

    vector_store = Chroma(
            collection_name="langchain_docs",
            persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
            embedding_function=embeddings,
            collection_metadata={"hnsw:space": "cosine"},
        )

    vector_store.add_documents(documents=docs, ids=[doc.metadata["source"] for doc in docs])


    retriever = vector_store.as_retriever(
                search_type="mmr", search_kwargs={"k": 1, "fetch_k": 5}
            )
    
    results = retriever.invoke("Which company provides AI services?")
    print("ChromaDB similarity search:")
    for result in results:
        print(" -", result.page_content)
        print("--------------------------------")

    # Similarity search
    # results = vector_store.similarity_search_with_score("Which company provides AI services?", k=4)
    # print("ChromaDB similarity search:")
    # for result, score in results:
    #     print(" -", result.page_content)
    #     print("Score:", score)
    #     print("--------------------------------")


    # vector_store.delete(ids=["openai", "google"])

    # results = vector_store.similarity_search("Which company provides AI services?", k=4)
    # print("ChromaDB similarity search after delete:")
    # for r in results:
    #     print(" -", r.page_content)
    #     print("--------------------------------")


    # vector_store.update_document(document_id="apple", document=Document(page_content="Apple is a company that do not provide AI services.", metadata={"source": "apple"}))

    # results = vector_store.similarity_search("Which company provides AI services?", k=4)
    # print("ChromaDB similarity search after update:")
    # for r in results:
    #     print(" -", r.page_content)
    #     print("--------------------------------")


except ImportError:
    print("ChromaDB: pip install langchain-community chromadb")
