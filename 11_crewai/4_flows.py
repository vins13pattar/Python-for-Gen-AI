"""
4. CrewAI Flows — Event-driven orchestration with @start, @listen, @router
   Official docs: https://docs.crewai.com/concepts/flows

Flows are the RECOMMENDED way to build production CrewAI applications.
While Crews handle agent collaboration, Flows handle the bigger picture:
  - Sequencing multiple steps (with or without agents)
  - Conditional branching (routing)
  - State management across steps
  - Mixing AI and non-AI logic (API calls, DB queries, etc.)

Key decorators:
  @start()          → marks the entry point(s) of the flow
  @listen(method)   → runs when the specified method completes
  @router(method)   → conditional branching based on return value

State management:
  - Unstructured : self.state is a plain dict (flexible, less safe)
  - Structured   : Flow[MyModel] uses a Pydantic BaseModel (type-safe)

This file demonstrates both simple and complex flows.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel
from litellm import completion


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 1: Simple Linear Flow (no agents, just flow logic)
# ═══════════════════════════════════════════════════════════════════
# This demonstrates the basic flow mechanics without any Crew.
# Steps: generate_topic → research_topic → write_summary

class SimpleFlow(Flow):
    """
    A simple 3-step flow that:
    1. Generates a random tech topic using an LLM
    2. Researches it (simulated)
    3. Writes a summary
    """

    @start()                    # ← This method runs first
    def generate_topic(self):
        """Step 1: Ask the LLM to suggest a trending tech topic."""
        print("📌 Step 1: Generating topic...")

        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": "Name one trending technology topic in 2025. Reply with just the topic name, nothing else."
            }],
        )
        topic = response.choices[0].message.content.strip()
        print(f"   Topic selected: {topic}")
        return topic            # ← return value is passed to listeners

    @listen(generate_topic)     # ← Runs after generate_topic completes
    def research_topic(self, topic: str):
        """Step 2: Research the topic (using LLM as a simulation)."""
        print(f"\n🔍 Step 2: Researching '{topic}'...")

        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Provide 3 key facts about {topic}. Be concise, one line each."
            }],
        )
        facts = response.choices[0].message.content.strip()
        print(f"   Found facts:\n{facts}")
        return facts

    @listen(research_topic)     # ← Runs after research_topic completes
    def write_summary(self, facts: str):
        """Step 3: Write a summary paragraph from the facts."""
        print(f"\n✍️  Step 3: Writing summary...")

        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Write a 2-sentence summary from these facts:\n{facts}"
            }],
        )
        summary = response.choices[0].message.content.strip()
        print(f"   Summary: {summary}")
        return summary


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 2: Flow with Structured State (Pydantic)
# ═══════════════════════════════════════════════════════════════════
# Using Flow[MyModel] gives you type-safe state via self.state

class ContentState(BaseModel):
    """Pydantic model defining the flow's state shape."""
    topic: str = ""
    quality_score: int = 0
    draft: str = ""
    final_output: str = ""
    route_taken: str = ""


class StatefulFlow(Flow[ContentState]):
    """
    A flow with structured state and conditional routing.
    
    Steps:
      1. pick_topic     → sets self.state.topic
      2. evaluate       → scores the topic quality (0-10)
      3. route_decision → if score >= 7: detailed path, else: simple path
      4a. detailed_path → writes a detailed article
      4b. simple_path   → writes a brief summary
    """

    @start()
    def pick_topic(self):
        """Initialize the flow by setting a topic in state."""
        print("📌 Step 1: Picking topic...")
        self.state.topic = "The Future of AI Agents"
        print(f"   Topic: {self.state.topic}")

    @listen(pick_topic)
    def evaluate(self):
        """Score the topic's trendiness (simulated with LLM)."""
        print("\n🎯 Step 2: Evaluating topic quality...")

        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Rate the trendiness of '{self.state.topic}' on a scale of 1-10. "
                    "Reply with JUST the number, nothing else."
                )
            }],
        )
        try:
            score = int(response.choices[0].message.content.strip())
        except ValueError:
            score = 7  # default if parsing fails

        self.state.quality_score = score
        print(f"   Quality score: {score}/10")

    @router(evaluate)           # ← ROUTER: conditional branching!
    def route_decision(self):
        """
        Route based on quality score.
        Returns a string that matches a @listen() label.
        """
        print(f"\n🔀 Router: Score is {self.state.quality_score}")
        if self.state.quality_score >= 7:
            print("   → Taking the DETAILED path")
            return "detailed"   # matches @listen("detailed")
        else:
            print("   → Taking the SIMPLE path")
            return "simple"     # matches @listen("simple")

    @listen("detailed")         # ← Only runs if router returns "detailed"
    def detailed_path(self):
        """Write a detailed article for high-quality topics."""
        print("\n📝 Detailed Path: Writing comprehensive article...")
        self.state.route_taken = "detailed"

        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    f"Write a detailed 200-word article about '{self.state.topic}'. "
                    "Include introduction, key points, and conclusion."
                )
            }],
        )
        self.state.final_output = response.choices[0].message.content.strip()

    @listen("simple")           # ← Only runs if router returns "simple"
    def simple_path(self):
        """Write a brief summary for lower-quality topics."""
        print("\n📝 Simple Path: Writing brief summary...")
        self.state.route_taken = "simple"

        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Write a 2-sentence summary about '{self.state.topic}'."
            }],
        )
        self.state.final_output = response.choices[0].message.content.strip()


# ═══════════════════════════════════════════════════════════════════
# RUN THE FLOWS
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # ── Example 1: Simple Linear Flow ──
    print("═" * 60)
    print("  EXAMPLE 1: Simple Linear Flow")
    print("═" * 60)

    simple_flow = SimpleFlow()
    result = simple_flow.kickoff()
    print(f"\n✅ Flow result: {result}")

    # ── Example 2: Stateful Flow with Routing ──
    print("\n\n" + "═" * 60)
    print("  EXAMPLE 2: Stateful Flow with Router")
    print("═" * 60)

    stateful_flow = StatefulFlow()
    stateful_flow.kickoff()

    # Access the final state
    print(f"\n✅ Final State:")
    print(f"   Topic:         {stateful_flow.state.topic}")
    print(f"   Quality Score:  {stateful_flow.state.quality_score}")
    print(f"   Route Taken:    {stateful_flow.state.route_taken}")
    print(f"   Output Preview: {stateful_flow.state.final_output[:200]}...")
