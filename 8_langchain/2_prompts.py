"""
2. Prompt Templates — Official docs: reference.langchain.com/python/langchain_core/prompts

ChatPromptTemplate: from_messages([(role, template), ...])
MessagesPlaceholder: inject conversation history
partial(): pre-fill variables
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

name = "Bob"
jobs = "help the user with their questions, and provide information about the user's questions., and be friendly and engaging."

prompt_template = PromptTemplate(
    template="You are a helpful AI bot. Your name is {name}. Your job is to to {jobs}.",
    input_variables=["name", "jobs"],
)

prompt_value = prompt_template.invoke({"name": name, "jobs": jobs})


print("PromptTemplate:", prompt_value)

# Basic ChatPromptTemplate
template = ChatPromptTemplate.from_messages([
    ("system", f"You are a helpful AI bot. Your name is {name}. Your job is to to {jobs}."),
    ("human", "{user_input}"),
])
prompt_value = template.invoke({"name": "Bob", "user_input": "What is your name?", "jobs": "help the user with their questions, and provide information about the user's questions., and be friendly and engaging."})
print("ChatPromptTemplate:", prompt_value.messages[-1].content)

# MessagesPlaceholder — conversation history
template_with_history = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI bot."),
    MessagesPlaceholder(variable_name="conversation"),
])
prompt_value = template_with_history.invoke({
    "conversation": [
        ("human", "Hi!"),
        ("ai", "How can I assist you today?"),
        ("human", "Can you make me an ice cream sundae?"),
        ("ai", "No."),
    ],
})
print("MessagesPlaceholder:", len(prompt_value.messages), "messages")

# Single variable — invoke with string directly
template_single = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI bot. Your name is Carl."),
    ("human", "{user_input}"),
])
prompt_value = template_single.invoke("Hello, there!")
print("Single variable:", prompt_value.messages[-1].content)

# partial() — pre-fill some variables
template_partial = ChatPromptTemplate.from_messages([
    ("system", "You answer in {language}."),
    ("human", "{input}"),
])
partial_prompt = template_partial.partial(language="French")
result = partial_prompt.invoke({"input": "Hello!"})
print("Partial:", result.messages[-1].content)
