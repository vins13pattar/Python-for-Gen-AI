"""
Analysis Crew — The core CrewAI crew for stock analysis.

Contains 6 agents working sequentially:
1. Market Data Analyst → fetches price data
2. Technical Analyst → calculates indicators
3. Fundamental Analyst → reviews financials
4. News Sentiment Analyst → analyzes news
5. Risk Analyst → identifies risks
6. Report Writer → generates final report
"""

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from stock_analysis_crew.tools.stock_price_tool import StockPriceTool
from stock_analysis_crew.tools.technical_indicator_tool import TechnicalIndicatorTool
from stock_analysis_crew.tools.financial_metrics_tool import FinancialMetricsTool
from stock_analysis_crew.tools.news_search_tool import NewsSearchTool


@CrewBase
class AnalysisCrew:
    """Stock Analysis Crew — 6 agents for comprehensive Indian stock analysis."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ── Agents ──────────────────────────────────────────────

    @agent
    def market_data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["market_data_analyst"],  # type: ignore[index]
            tools=[StockPriceTool()],
            verbose=True,
        )

    @agent
    def technical_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_analyst"],  # type: ignore[index]
            tools=[TechnicalIndicatorTool()],
            verbose=True,
        )

    @agent
    def fundamental_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["fundamental_analyst"],  # type: ignore[index]
            tools=[FinancialMetricsTool()],
            verbose=True,
        )

    @agent
    def news_sentiment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["news_sentiment_analyst"],  # type: ignore[index]
            tools=[NewsSearchTool(), SerperDevTool()],
            verbose=True,
        )

    @agent
    def risk_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["risk_analyst"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["report_writer"],  # type: ignore[index]
            verbose=True,
        )

    # ── Tasks ──────────────────────────────────────────────

    @task
    def market_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["market_data_task"],  # type: ignore[index]
        )

    @task
    def technical_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["technical_analysis_task"],  # type: ignore[index]
        )

    @task
    def fundamental_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["fundamental_analysis_task"],  # type: ignore[index]
        )

    @task
    def news_sentiment_task(self) -> Task:
        return Task(
            config=self.tasks_config["news_sentiment_task"],  # type: ignore[index]
        )

    @task
    def risk_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["risk_analysis_task"],  # type: ignore[index]
        )

    @task
    def report_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config["report_generation_task"],  # type: ignore[index]
            output_file="output/report.md",
        )

    # ── Crew ──────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        """Creates the Stock Analysis Crew with sequential process."""
        return Crew(
            agents=self.agents,   # Auto-collected by @agent decorator
            tasks=self.tasks,     # Auto-collected by @task decorator
            process=Process.sequential,
            verbose=True,
        )
