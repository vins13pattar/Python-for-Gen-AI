from langchain.agents.middleware import AgentMiddleware, AgentState, wrap_model_call
from langchain.agents import create_agent
from langgraph.runtime import Runtime
from typing import Any
import time

from dotenv import load_dotenv
load_dotenv()


class LoggingMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        msg_count = len(state["messages"])
        print(f"Calling model with {msg_count} messages")
        return None  # no state update needed

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        last = state["messages"][-1].content
        print(f"Model responded: {last[:80]}...")
        return None


@wrap_model_call
def retry_model(request: ModelRequest, handler) -> ModelResponse:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return handler(request)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            print("Retrying...")
            time.sleep(1)   # Added time to make it realistic

agent = create_agent(
    model="gpt-5-mini-6526567",
    middleware=[LoggingMiddleware(), retry_model],
    tools=[],
)

result = agent.invoke(
    {"messages": [{"role": "human", "content": "Hello there"}]},
    stream=True,
)

