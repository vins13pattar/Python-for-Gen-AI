"""
6. CrewAI Production Pattern — Flows Orchestrating Multiple Crews
   Official docs: https://docs.crewai.com/concepts/flows

This is the RECOMMENDED production architecture for CrewAI:
  Flow (orchestration layer)
    └── Crew 1 (research team)
    └── Crew 2 (analysis team)
    └── Crew 3 (content team)

Why Flows + Crews together?
  - Flows handle the big picture: sequencing, routing, state
  - Crews handle agent collaboration within each step
  - You can mix AI (crews) and non-AI (Python logic) steps
  - State flows automatically between steps

This file builds a realistic content pipeline:
  Step 1: Generate topic ideas (Flow logic + LLM)
  Step 2: Research crew deep-dives into the chosen topic
  Step 3: Writing crew produces the final article
  Step 4: Save output to a file (plain Python, no AI)
"""

import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel
from litellm import completion


# ═══════════════════════════════════════════════════════════════════
# 1. STATE MODEL — shared across all flow steps
# ═══════════════════════════════════════════════════════════════════

class PipelineState(BaseModel):
    """State that flows through the entire pipeline."""
    topic: str = ""
    research_output: str = ""
    article: str = ""
    word_count: int = 0
    quality: str = ""      # "publish" or "revise"
    saved_to: str = ""


# ═══════════════════════════════════════════════════════════════════
# 2. DEFINE AGENTS (reusable across crews)
# ═══════════════════════════════════════════════════════════════════

# -- Research Crew Agents --
lead_researcher = Agent(
    role="Lead Researcher",
    goal="Conduct thorough research and gather comprehensive information",
    backstory=(
        "You are a meticulous researcher who leaves no stone unturned. "
        "You gather data from multiple angles and organize findings clearly."
    ),
    verbose=True,
    allow_delegation=False,
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Verify research claims and ensure accuracy",
    backstory=(
        "You are a skeptical fact-checker who questions every claim. "
        "You verify data, check for contradictions, and flag uncertainties."
    ),
    verbose=True,
    allow_delegation=False,
)

# -- Writing Crew Agents --
senior_writer = Agent(
    role="Senior Writer",
    goal="Write compelling, well-structured articles",
    backstory=(
        "You are an award-winning tech writer known for making complex "
        "topics accessible. Your articles are engaging and informative."
    ),
    verbose=True,
    allow_delegation=False,
)

editor = Agent(
    role="Editor",
    goal="Polish articles for clarity, flow, and impact",
    backstory=(
        "You are a seasoned editor who transforms good writing into great writing. "
        "You focus on structure, tone, and readability."
    ),
    verbose=True,
    allow_delegation=False,
)


# ═══════════════════════════════════════════════════════════════════
# 3. CREW FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
# Instead of creating crews at module level, we use factory functions
# so we can pass dynamic inputs (like the topic from state).

def create_research_crew(topic: str) -> Crew:
    """Create a research crew for the given topic."""

    research_task = Task(
        description=(
            f"Conduct comprehensive research about: '{topic}'. "
            "Cover: current state, key developments, challenges, "
            "and future outlook. Provide specific examples and data."
        ),
        expected_output=(
            "A detailed research document with:\n"
            "- Overview of the topic\n"
            "- 5 key developments with examples\n"
            "- 3 main challenges\n"
            "- Future outlook"
        ),
        agent=lead_researcher,
    )

    verification_task = Task(
        description=(
            "Review the research findings and verify the key claims. "
            "Flag any statements that need citations or seem uncertain. "
            "Add confidence levels (High/Medium/Low) to each finding."
        ),
        expected_output=(
            "Verified research with confidence levels for each finding. "
            "Any flagged uncertainties should be noted."
        ),
        agent=fact_checker,
        context=[research_task],
    )

    return Crew(
        agents=[lead_researcher, fact_checker],
        tasks=[research_task, verification_task],
        process=Process.sequential,
        verbose=True,
    )


def create_writing_crew(topic: str, research: str) -> Crew:
    """Create a writing crew that uses research to produce an article."""

    writing_task = Task(
        description=(
            f"Write an engaging 500-word article about '{topic}' "
            f"using the following research:\n\n{research[:2000]}\n\n"
            "Use a professional but accessible tone. "
            "Include subheadings, examples, and a strong conclusion."
        ),
        expected_output="A polished 500-word article in Markdown format.",
        agent=senior_writer,
    )

    editing_task = Task(
        description=(
            "Edit the article for:\n"
            "- Clarity and readability\n"
            "- Grammar and style consistency\n"
            "- Logical flow between sections\n"
            "- Strong opening and closing\n"
            "Make the edits directly — return the final polished version."
        ),
        expected_output="The final edited article, ready for publication.",
        agent=editor,
        context=[writing_task],
    )

    return Crew(
        agents=[senior_writer, editor],
        tasks=[writing_task, editing_task],
        process=Process.sequential,
        verbose=True,
    )


# ═══════════════════════════════════════════════════════════════════
# 4. THE FLOW — orchestrates everything
# ═══════════════════════════════════════════════════════════════════

class ContentPipeline(Flow[PipelineState]):
    """
    Production content pipeline:
      generate_topic → research (Crew) → write (Crew) → quality_check → save
    """

    @start()
    def generate_topic(self):
        """Step 1: Generate a topic using an LLM (no agents needed)."""
        print("\n📌 STEP 1: Generating topic...")

        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": (
                    "Suggest one specific, interesting topic for a tech article "
                    "about AI in 2025. Reply with just the topic, nothing else."
                )
            }],
        )
        self.state.topic = response.choices[0].message.content.strip()
        print(f"   ✅ Topic: {self.state.topic}")

    @listen(generate_topic)
    def run_research(self):
        """Step 2: Spin up a Research Crew to investigate the topic."""
        print(f"\n🔍 STEP 2: Research Crew investigating '{self.state.topic}'...")

        # Create and run the research crew
        research_crew = create_research_crew(self.state.topic)
        result = research_crew.kickoff()

        # Store result in state for the next step
        self.state.research_output = str(result)
        print(f"   ✅ Research complete ({len(self.state.research_output)} chars)")

    @listen(run_research)
    def run_writing(self):
        """Step 3: Spin up a Writing Crew to produce the article."""
        print(f"\n✍️  STEP 3: Writing Crew producing article...")

        # Create and run the writing crew
        writing_crew = create_writing_crew(
            self.state.topic,
            self.state.research_output
        )
        result = writing_crew.kickoff()

        self.state.article = str(result)
        self.state.word_count = len(self.state.article.split())
        print(f"   ✅ Article complete ({self.state.word_count} words)")

    @router(run_writing)
    def quality_check(self):
        """Step 4: Route based on article quality (word count check)."""
        print(f"\n🔀 STEP 4: Quality check...")
        print(f"   Word count: {self.state.word_count}")

        if self.state.word_count >= 100:
            print("   ✅ Meets quality bar → publishing")
            return "publish"
        else:
            print("   ⚠️  Too short → needs revision")
            return "revise"

    @listen("publish")
    def save_article(self):
        """Step 5a: Save the article to a file."""
        print(f"\n💾 STEP 5: Saving article...")

        filename = f"article_{uuid.uuid4().hex[:8]}.md"
        filepath = os.path.join(os.path.dirname(__file__) or ".", filename)

        with open(filepath, "w") as f:
            f.write(f"# {self.state.topic}\n\n")
            f.write(self.state.article)

        self.state.saved_to = filepath
        self.state.quality = "published"
        print(f"   ✅ Saved to: {filepath}")

    @listen("revise")
    def request_revision(self):
        """Step 5b: Flag for revision (in production, loop back)."""
        print(f"\n🔄 STEP 5: Flagged for revision")
        self.state.quality = "needs_revision"


# ═══════════════════════════════════════════════════════════════════
# 5. RUN THE PIPELINE
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("  CONTENT PIPELINE — Flow + Multiple Crews")
    print("  Topic → Research Crew → Writing Crew → Quality → Save")
    print("═" * 60)

    pipeline = ContentPipeline()
    pipeline.kickoff()

    # Final report
    print("\n" + "═" * 60)
    print("  PIPELINE COMPLETE")
    print("═" * 60)
    print(f"  Topic:        {pipeline.state.topic}")
    print(f"  Word count:   {pipeline.state.word_count}")
    print(f"  Quality:      {pipeline.state.quality}")
    print(f"  Saved to:     {pipeline.state.saved_to or 'N/A'}")
    print(f"\n  Article preview:")
    print(f"  {pipeline.state.article[:300]}...")
