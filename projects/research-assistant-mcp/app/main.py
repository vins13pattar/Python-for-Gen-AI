"""
Research Assistant System — CLI Entry Point

Usage:
    # Run with a topic (mock mode, no API key needed)
    uv run python app/main.py --topic "Impact of AI agents on software development"

    # Export report to specific file
    uv run python app/main.py --topic "MCP for multi-agent systems" --export report.md

    # Enable debug mode (verbose agent message logging)
    uv run python app/main.py --topic "Agentic AI" --debug

    # Use real LLM (requires OPENAI_API_KEY in .env)
    USE_MOCK_LLM=false uv run python app/main.py --topic "AI in healthcare"
"""

import sys
import logging
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint

from app.config import config

# ── CLI App Setup ─────────────────────────────────────────────────────────────
app = typer.Typer(
    name="research-assistant",
    help="Research Assistant System — Multi-Agent MCP Demo",
    add_completion=False,
)
console = Console()


def _setup_logging(debug: bool) -> None:
    """Configure logging level."""
    level = logging.DEBUG if debug else getattr(logging, config.LOG_LEVEL, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # Quiet noisy third-party loggers
    for noisy in ["httpx", "httpcore", "openai", "urllib3"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)


def _print_banner(topic: str, session_id: str) -> None:
    """Print the startup banner."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]🔬 Research Assistant System[/bold cyan]\n"
            f"[dim]Multi-Agent MCP Demo | LangGraph + CrewAI[/dim]\n\n"
            f"[bold]Topic:[/bold] {topic}\n"
            f"[dim]Session: {session_id}[/dim]",
            border_style="cyan",
        )
    )
    console.print()


def _print_config_summary(debug: bool) -> None:
    """Print configuration summary."""
    table = Table(title="Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("LLM Mode", "🤖 Mock (demo)" if config.USE_MOCK_LLM else f"✨ OpenAI {config.OPENAI_MODEL}")
    table.add_row("Embeddings", "🎲 Mock vectors" if config.USE_MOCK_EMBEDDINGS else f"✨ OpenAI {config.EMBEDDING_MODEL}")
    table.add_row("Max Critic Retries", str(config.MAX_CRITIC_RETRIES))
    table.add_row("Debug Mode", "✅ ON" if debug else "❌ OFF")

    console.print(table)
    console.print()


def _print_agent_progress(step: int, agent_name: str, status: str = "running") -> None:
    """Print agent progress."""
    icons = {
        "planner": "📋",
        "retriever": "🔍",
        "embedding": "🧮",
        "analyst": "🔬",
        "critic": "⚖️",
        "writer": "✍️",
    }
    color_map = {"running": "yellow", "done": "green", "retry": "orange1"}
    icon = icons.get(agent_name.lower(), "🤖")
    color = color_map.get(status, "white")
    console.print(f"  [{color}]{icon} Step {step}: {agent_name.title()} Agent[/{color}]")


def _print_results_summary(exported: dict, elapsed: float) -> None:
    """Print final results summary."""
    console.print()
    console.print(
        Panel.fit(
            "[bold green]✅ Research Completed Successfully![/bold green]",
            border_style="green",
        )
    )
    console.print()
    console.print(f"[bold]⏱  Elapsed:[/bold] {elapsed:.1f}s")
    console.print()
    console.print("[bold cyan]📁 Generated Files:[/bold cyan]")

    for key, path in exported.items():
        size = path.stat().st_size if path.exists() else 0
        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"
        console.print(f"   [green]✓[/green] {path}  [dim]({size_str})[/dim]")

    console.print()


@app.command()
def main(
    topic: Optional[str] = typer.Option(
        None,
        "--topic",
        "-t",
        help="Research topic to investigate.",
        show_default=False,
    ),
    export: Optional[Path] = typer.Option(
        None,
        "--export",
        "-e",
        help="Export final report to this file path (e.g. report.md).",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug mode — prints detailed agent messages.",
    ),
    show_crew: bool = typer.Option(
        False,
        "--show-crew",
        help="Show CrewAI agent role definitions.",
    ),
    show_messages: bool = typer.Option(
        False,
        "--show-messages",
        help="Print all agent MCP messages after completion.",
    ),
) -> None:
    """
    Research Assistant System — Multi-Agent MCP Demo.

    Runs a 6-agent research pipeline on your topic using LangGraph,
    CrewAI role definitions, and MCP-style structured messaging.
    """
    import time

    _setup_logging(debug)

    # ── Topic input ────────────────────────────────────────────────────────
    if not topic:
        topic = config.RESEARCH_TOPIC
        if not topic:
            topic = typer.prompt(
                "📚 Enter your research topic",
                default="Impact of AI agents on software development",
            )

    topic = topic.strip()
    if not topic:
        console.print("[red]❌ Error: Research topic cannot be empty.[/red]")
        raise typer.Exit(1)

    # ── Config validation ──────────────────────────────────────────────────
    try:
        config.validate()
    except EnvironmentError as e:
        console.print(f"[red]❌ Configuration Error: {e}[/red]")
        raise typer.Exit(1)

    # ── Session setup ──────────────────────────────────────────────────────
    session_id = f"{config.SESSION_PREFIX}_{uuid.uuid4().hex[:8]}"
    _print_banner(topic, session_id)
    _print_config_summary(debug)

    # ── Show CrewAI agents if requested ───────────────────────────────────
    if show_crew:
        from app.crew.crew_config import get_crew_agents
        from app.crew.tasks import get_task_definitions

        crew_table = Table(
            title="CrewAI Agent Roles",
            show_header=True,
            header_style="bold blue",
        )
        crew_table.add_column("Agent", style="cyan", width=25)
        crew_table.add_column("Role", style="yellow", width=25)
        crew_table.add_column("Goal Preview", style="white", width=50)

        agents_cfg = get_crew_agents()
        for name, cfg in agents_cfg.items():
            crew_table.add_row(name, cfg["role"], cfg["goal"][:80] + "...")

        console.print(crew_table)
        console.print()

    # ── Initialize state ───────────────────────────────────────────────────
    from app.state.state_store import state_store

    initial_state = state_store.initialize(
        session_id=session_id,
        topic=topic,
        debug=debug,
    )

    # ── Run LangGraph workflow ─────────────────────────────────────────────
    from app.graph.workflow import get_workflow

    console.print("[bold]🚀 Starting Research Pipeline...[/bold]")
    console.print()

    workflow = get_workflow()
    start_time = time.time()

    try:
        # Stream events from LangGraph for progress display
        step = 1
        node_display_names = {
            "planner": "Planner",
            "retriever": "Retriever",
            "embedding": "Embedding",
            "analyst": "Analyst",
            "critic": "Critic",
            "writer": "Writer",
        }

        final_state = None
        for event in workflow.stream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                display = node_display_names.get(node_name, node_name.title())
                status = "done"
                if node_name == "critic":
                    critique_status = node_output.get("critique_status", "approved")
                    status = "retry" if critique_status == "needs_improvement" else "done"
                _print_agent_progress(step, display, status)

                if status == "retry":
                    console.print(
                        f"    [orange1]↩ Critic requested more context — retrying retrieval[/orange1]"
                    )
                step += 1

            final_state = node_output

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Interrupted by user.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Workflow error: {e}[/red]")
        if debug:
            import traceback
            traceback.print_exc()
        # Try to export partial state
        try:
            state_store.export_all()
        except Exception:
            pass
        raise typer.Exit(1)

    elapsed = time.time() - start_time

    # ── Export outputs ─────────────────────────────────────────────────────
    exported = state_store.export_all()

    # Additional export path if --export flag used
    if export and "final_report" in exported:
        import shutil
        shutil.copy(exported["final_report"], export)
        exported["custom_export"] = Path(export)
        console.print(f"[green]✓ Report also exported to: {export}[/green]")

    _print_results_summary(exported, elapsed)

    # ── Show messages if requested ────────────────────────────────────────
    if show_messages:
        current_state = state_store.get_state()
        messages = current_state["agent_messages"]

        console.print(f"[bold cyan]📨 Agent Messages ({len(messages)} total):[/bold cyan]")
        msg_table = Table(show_header=True, header_style="bold")
        msg_table.add_column("#", width=3)
        msg_table.add_column("From", style="cyan", width=18)
        msg_table.add_column("To", style="yellow", width=18)
        msg_table.add_column("Type", style="green", width=28)
        msg_table.add_column("Timestamp", style="dim", width=12)

        for i, msg in enumerate(messages, 1):
            ts = msg.get("timestamp", "")[:19].replace("T", " ")
            msg_table.add_row(
                str(i),
                msg.get("sender_agent", "?"),
                msg.get("receiver_agent", "?"),
                msg.get("message_type", "?"),
                ts,
            )

        console.print(msg_table)

    console.print("[dim]Run with --show-messages to see all agent messages.[/dim]")
    console.print("[dim]Run with --show-crew to see CrewAI agent definitions.[/dim]")
    console.print()


if __name__ == "__main__":
    app()
