#!/usr/bin/env python
"""
Stock Analysis Crew — Flow Orchestration

This is the main entry point for the application.
The StockAnalysisFlow validates the stock symbol, runs the AnalysisCrew,
and saves the final report.
"""

from pathlib import Path

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from stock_analysis_crew.crews.analysis_crew.analysis_crew import AnalysisCrew
from stock_analysis_crew.utils.validators import validate_symbol
from stock_analysis_crew.utils.disclaimer import DISCLAIMER


class StockAnalysisState(BaseModel):
    """State model for the Stock Analysis Flow."""

    symbol: str = ""
    analysis_type: str = "detailed"
    period: str = "1y"
    report: str = ""
    error: str = ""
    is_valid: bool = False


class StockAnalysisFlow(Flow[StockAnalysisState]):
    """
    Stock Analysis Flow — Orchestrates the analysis pipeline.

    Steps:
    1. validate_input → Validates the stock symbol
    2. run_analysis → Kicks off the AnalysisCrew (6 agents)
    3. save_report → Saves the report to output/report.md
    """

    @start()
    def validate_input(self):
        """Validate the stock symbol before running analysis."""
        print(f"\n{'='*60}")
        print(f"  Stock Analysis Crew — Analyzing {self.state.symbol}")
        print(f"{'='*60}\n")

        if not self.state.symbol:
            self.state.error = "No stock symbol provided."
            self.state.is_valid = False
            print(f"❌ Error: {self.state.error}")
            return

        # Normalize symbol
        self.state.symbol = self.state.symbol.strip().upper()

        # Validate
        is_valid, message = validate_symbol(self.state.symbol)
        self.state.is_valid = is_valid

        if not is_valid:
            self.state.error = message
            print(f"❌ Validation failed: {message}")
        else:
            print(f"✅ Symbol validated: {self.state.symbol}")

    @listen(validate_input)
    def run_analysis(self):
        """Run the AnalysisCrew if the symbol is valid."""
        if not self.state.is_valid:
            print("⏭️  Skipping analysis due to validation error.")
            return

        print(f"\n🚀 Starting analysis for {self.state.symbol}...")
        print(f"   Analysis type: {self.state.analysis_type}")
        print(f"   Period: {self.state.period}")
        print()

        try:
            result = (
                AnalysisCrew()
                .crew()
                .kickoff(
                    inputs={
                        "symbol": self.state.symbol,
                    }
                )
            )
            self.state.report = result.raw
            print("\n✅ Analysis complete!")

        except Exception as e:
            self.state.error = f"Analysis failed: {str(e)}"
            print(f"\n❌ {self.state.error}")

    @listen(run_analysis)
    def save_report(self):
        """Save the final report to output/report.md."""
        if not self.state.report:
            if self.state.error:
                print(f"\n❌ No report generated. Error: {self.state.error}")
            return

        # Append disclaimer if not already present
        if "Disclaimer" not in self.state.report:
            self.state.report += f"\n\n{DISCLAIMER}"

        # Save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "report.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.state.report)

        print(f"\n📄 Report saved to {output_path}")
        print(f"{'='*60}")
        print("  Stock Analysis Complete!")
        print(f"{'='*60}\n")


def kickoff():
    """Run the Stock Analysis Flow from CLI."""
    symbol = input("\nEnter Indian stock symbol (e.g., RELIANCE.NS): ").strip()

    if not symbol:
        symbol = "RELIANCE.NS"
        print(f"Using default symbol: {symbol}")

    flow = StockAnalysisFlow()
    flow.kickoff(inputs={"symbol": symbol})

    if flow.state.report:
        print("\n" + "=" * 60)
        print("  GENERATED REPORT PREVIEW")
        print("=" * 60)
        # Show first 500 chars
        preview = flow.state.report[:500]
        print(preview)
        if len(flow.state.report) > 500:
            print(f"\n... [Report continues — {len(flow.state.report)} chars total]")
            print("Full report saved to output/report.md")


def plot():
    """Generate and display the flow diagram."""
    flow = StockAnalysisFlow()
    flow.plot()


def run_with_trigger():
    """Run the flow with trigger payload (for programmatic use)."""
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. "
            "Usage: run_with_trigger '{\"symbol\": \"RELIANCE.NS\"}'"
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument.")

    flow = StockAnalysisFlow()
    result = flow.kickoff(inputs=trigger_payload)
    return result


if __name__ == "__main__":
    kickoff()
