import streamlit as st
import uuid
from langchain_core.messages import HumanMessage
from src.graph import app
from src.config import CHROMA_DB_DIR
import os

st.set_page_config(page_title="MicroDegree Support Bot", page_icon="🤖")

st.title("MicroDegree Customer Support Chatbot")
st.markdown("I can help you with MicroDegree courses, certificates, Kannada learning, and contact details. How can I help you today?")

# Check if ChromaDB exists
if not os.path.exists(CHROMA_DB_DIR):
    st.error(f"Vector Database not found at {CHROMA_DB_DIR}. Please run `python -m src.ingest` first.")
    st.stop()

# Initialize session state for memory
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about MicroDegree..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            # The langgraph app returns the final state
            try:
                final_state = app.invoke(
                    {"messages": [HumanMessage(content=prompt)]}, 
                    config=config
                )
                
                answer = final_state.get("answer", "I'm sorry, an error occurred.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Add a clear chat button in the sidebar
with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
