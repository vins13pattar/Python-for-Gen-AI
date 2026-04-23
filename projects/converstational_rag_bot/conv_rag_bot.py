"""
Conversational RAG bot (LangChain + Chroma + OpenAI).

End-to-end flow (same behavior as before; reorganized for reading):

  1) Ingest fixed tutorial snippets into a persisted Chroma collection (embeddings).
  2) Build an LCEL chain: one preparation step turns the turn dict into prompt fields
     (context, question, history), then chat prompt -> LLM -> text.
  3) Wrap that chain with RunnableWithMessageHistory so each session_id gets its own
     ChatMessageHistory: past turns are injected under the "history" key, and new
     user/assistant turns are appended automatically after each invoke.

The preparation step reads turn["question"] as a string before calling the retriever,
so Chroma never receives the whole {"question", "history"} dict as a "query document".
"""

from __future__ import annotations

import os
from typing import Any, List

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableLambda, RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# 1) Knowledge base (static documents used for retrieval)
# ---------------------------------------------------------------------------

DOCS = [
    Document(page_content="LangChain is a framework for building LLM-powered applications using composable components.", metadata={"source": "langchain", "id": "doc1"}),
    Document(page_content="Embeddings transform text into dense numeric vectors in high-dimensional space, capturing semantic meaning.", metadata={"source": "embeddings", "id": "doc2"}),
    Document(page_content="SentenceTransformer all-MiniLM-L6-v2 produces 384-dimensional embeddings efficiently on CPU.", metadata={"source": "sentence_transformer", "id": "doc3"}),
    Document(page_content="OpenAI text-embedding-3-small produces 1536-dimensional embeddings with high semantic accuracy.", metadata={"source": "openai", "id": "doc4"}),
    Document(page_content="Vector stores index embeddings for fast approximate nearest-neighbor search at scale.", metadata={"source": "vector_store", "id": "doc5"}),
    Document(page_content="Chroma is a local persistent vector database. FAISS is optimized for in-memory similarity search.", metadata={"source": "chroma", "id": "doc6"}),
    Document(page_content="Cosine similarity measures the angle between two vectors to determine their semantic closeness.", metadata={"source": "cosine_similarity", "id": "doc7"}),
    Document(page_content="MMR stands for Max Marginal Relevance. It retrieves results that are both relevant and diverse.", metadata={"source": "mmr", "id": "doc8"}),
    Document(page_content="Multi-Query Retriever uses an LLM to generate multiple phrasings of the original query to broaden recall.", metadata={"source": "multi_query_retriever", "id": "doc9"}),
    Document(page_content="RunnableWithMessageHistory wraps any LCEL chain and automatically injects per-session chat history.", metadata={"source": "runnable_with_message_history", "id": "doc10"}),
    Document(page_content="RAG stands for Retrieval Augmented Generation: retrieved context chunks are injected into the LLM prompt.", metadata={"source": "rag", "id": "doc11"}),
    Document(page_content="ChatMessageHistory stores a list of HumanMessage and AIMessage objects for a single session.", metadata={"source": "chat_message_history", "id": "doc12"}),
    Document(page_content="MessagesPlaceholder in a ChatPromptTemplate reserves a slot where the session history is injected.", metadata={"source": "messages_placeholder", "id": "doc13"}),
    Document(page_content="LCEL (LangChain Expression Language) uses the pipe operator | to chain runnables together.", metadata={"source": "lcel", "id": "doc14"}),
]

# ---------------------------------------------------------------------------
# 2) In-memory chat transcripts (one ChatMessageHistory per session_id)
# ---------------------------------------------------------------------------

message_history = ChatMessageHistory()
message_history.add_messages([
        HumanMessage(content="What is LLM?"),
        AIMessage(content="LLM is a type of machine learning model that is trained to understand and generate natural language."),
        
])

in_memory_store = {
    "session-123456": message_history,
}


def get_history(session_id: str) -> ChatMessageHistory:
    """Factory used by RunnableWithMessageHistory to load/save messages for a session."""
    if session_id not in in_memory_store:
        in_memory_store[session_id] = ChatMessageHistory()
    return in_memory_store[session_id]


# ---------------------------------------------------------------------------
# 3) Vector store: embed DOCS and persist to disk (Chroma)
# ---------------------------------------------------------------------------

def build_vector_store() -> Chroma:
    """
    Open (or create) a Chroma collection and upsert DOCS.

    Collection name and disk path come from env so you can swap environments
    without editing code. Stable string ids align with metadata['id'] on each Document.
    """
    vector_store = Chroma(
        collection_name=os.getenv("CHROMA_COLLECTION_NAME"),
        persist_directory=os.getenv("CHROMA_PERSIST_DIRECTORY"),
        collection_metadata={"hnsw:space": "cosine"},
    )
    vector_store.add_documents(
    documents=DOCS + [Document(page_content="Langchain is a framework for building LLM-powered applications using composable components.", metadata={"source": "langchain", "id": "doc15"})],
        ids=[doc.metadata["id"] for doc in DOCS],
    )
    return vector_store


# ---------------------------------------------------------------------------
# 4) Retrieval helpers
# ---------------------------------------------------------------------------

def retrieve_documents(retrieval_type: str, vector_store: Chroma, question: str) -> List[Document]:
    """
    Run LangChain's vector-store retriever for a plain-text question.

    retrieval_type selects the search strategy (same three modes as before).
    """
    if retrieval_type == "similarity":
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    elif retrieval_type == "mmr":
        retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 3})
    elif retrieval_type == "multi_query":
        retriever = vector_store.as_retriever(search_type="multi_query", search_kwargs={"k": 2})
    else:
        raise ValueError(f"Invalid retrieval_type: {retrieval_type}")
    return retriever.invoke(question)


def format_docs(docs: List[Document]) -> str:
    """Flatten retrieved Document objects into one system-prompt friendly block."""
    return "\n".join(d.page_content for d in docs)


def make_prepare_prompt_inputs(vector_store: Chroma, retrieval_type: str) -> Runnable:
    """
    Returns a Runnable that maps one "turn" dict -> the variables ChatPromptTemplate expects.

    Input shape (from RunnableWithMessageHistory, after it injects history):
      {"question": "<user string>", "history": [<prior messages>]}

    Output shape:
      {"context": "<joined retrieval text>", "question": "<same string>", "history": [...]}
    """

    def prepare_prompt_inputs(turn: dict[str, Any]) -> dict[str, Any]:
        question = turn["question"]
        history = turn.get("history", [])
        docs = retrieve_documents(retrieval_type, vector_store, question)
        return {
            "context": format_docs(docs),
            "question": question,
            "history": history,
        }

    return RunnableLambda(prepare_prompt_inputs)


# ---------------------------------------------------------------------------
# 5) RAG + memory chain
# ---------------------------------------------------------------------------

def build_rag_chain(vector_store: Chroma, retrieval_type: str, llm: ChatOpenAI) -> RunnableWithMessageHistory:
    """
    Compose: prepare prompt inputs -> chat prompt -> LLM -> string, then wrap with history.

    Inner runnable input (dict):
      - "question": str — latest user message for retrieval + final human template slot
      - "history": list[BaseMessage] — injected by RunnableWithMessageHistory before the inner chain runs

    Inner runnable output: str (assistant reply). The wrapper records user + assistant
    messages into the session history returned by get_history(session_id).
    """
    prepare_inputs = make_prepare_prompt_inputs(vector_store, retrieval_type)

    rag_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful Langchain tutor that answers questions based on the context provided. If you are not sure about the answer, say 'I don't know.'. \nContext:\n{context}",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ],
    )

    answer_chain = prepare_inputs | rag_prompt | llm | StrOutputParser()

    return RunnableWithMessageHistory(
        answer_chain, #question, history
        get_history,
        input_messages_key="question",
        history_messages_key="history",
    )


# ---------------------------------------------------------------------------
# 6) CLI entrypoint
# ---------------------------------------------------------------------------

def run_bot(session_id: str) -> None:
    """Interactive loop: type 'exit' to quit. Uses a fixed retrieval_type for this demo."""
    vector_store = build_vector_store()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    rag_chain = build_rag_chain(vector_store, "similarity", llm)

    while True:
        question = input("Enter a question: ")
        if question == "exit":
            break
        response = rag_chain.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}},
        )
        print(response)


if __name__ == "__main__":
    run_bot("session-123456")
