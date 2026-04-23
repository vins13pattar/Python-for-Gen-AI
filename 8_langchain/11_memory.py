"""
10. Memory & History — Session-based conversation persistence
Based on LangChain v0.3 Components Guide

Key concepts:
- RunnableWithMessageHistory — wraps any LCEL chain
- ChatMessageHistory — in-memory (development)
- RedisChatMessageHistory — persistent across restarts
"""
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

try:
    from langchain_community.chat_message_histories import (
        ChatMessageHistory,
        RedisChatMessageHistory,
    )
    from langchain_core.runnables.history import RunnableWithMessageHistory

    # Store: session_id -> ChatMessageHistory

    history_user_42 = ChatMessageHistory()
    history_user_42.add_messages(
        [
            AIMessage(content="What is your favorite food?"),
            HumanMessage(content="My favorite food is pizza."),
            AIMessage(content="What is your favorite color?"),
            HumanMessage(content="My favorite color is blue."),
            AIMessage(content="What is your favorite car?"),
            HumanMessage(content="My favorite car is a Tesla."),
            AIMessage(content="What is your favorite place?"),
            HumanMessage(content="My favorite place is Paris."),
            AIMessage(content="What is your favorite hangout spot?"),
            HumanMessage(content="My favorite hangout spot is the park."),
        ]
    )

    in_memory_store = {
        "window-user": history_user_42
    }

    def get_history(session_id: str):
        if session_id not in in_memory_store:
            in_memory_store[session_id] = ChatMessageHistory()
        return in_memory_store[session_id]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    chain = prompt | llm | StrOutputParser()

    chain_with_memory = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    print("\n=== Example 1: In-memory session history ===")
    session_a = {"configurable": {"session_id": "user-42"}}

    # r1 = chain_with_memory.invoke({"input": "What is my favorite food?"}, session_a)
    # print("R1:", r1)

    # r2 = chain_with_memory.invoke({"input": "What is my favorite color?"}, session_a)
    # print("R2:", r2)

    def get_windowed_history(session_id: str):
        if session_id not in in_memory_store:
            in_memory_store[session_id] = ChatMessageHistory()

        # Keep only the last 2 messages so context does not grow unbounded.
        in_memory_store[session_id].messages = in_memory_store[session_id].messages[-6:]
        print("Windowed history:", in_memory_store[session_id].messages)
        return in_memory_store[session_id]

    chain_with_window_memory = RunnableWithMessageHistory(
        chain,
        get_windowed_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    user_42_session_1 = {"configurable": {"session_id": "session-123456"}}
    user_42_session_2 = {"configurable": {"session_id": "session-234456"}}
    user_42_session_3 = {"configurable": {"session_id": "session-345456"}}

    r1 = chain_with_window_memory.invoke({"input": "what is my favorite car?"}, user_42_session_1)
    print("R1 (what is my favorite car?):", r1)


    print("\n=== Example 3: Redis persistent history (optional) ===")
    try:
        redis_url = "redis://localhost:6379/0"

        def get_redis_history(session_id: str):
            return RedisChatMessageHistory(session_id=session_id, url=redis_url)

        chain_with_redis_memory = RunnableWithMessageHistory(
            chain,
            get_redis_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        redis_config = {"configurable": {"session_id": "redis-user-1"}}
        print("Redis R1:", chain_with_redis_memory.invoke({"input": "Remember: I live in Hyderabad."}, redis_config))
        print("Redis R2:", chain_with_redis_memory.invoke({"input": "Where do I live?"}, redis_config))
    except Exception as redis_error:
        print("Redis example skipped (start Redis + install redis client):", redis_error)

except ImportError:
    print("Memory examples require: pip install langchain-community redis")
