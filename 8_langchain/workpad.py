from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Embed multiple documents
texts = [
    "RAG is retrieval-augmented generation.",
    "LCEL is LangChain's pipe syntax.",
]
doc_vectors = embeddings.embed_documents(texts)
print("Documents embedded:", len(doc_vectors), "x", len(doc_vectors[0]), "dims")