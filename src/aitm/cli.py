"""CLI entry point for AI-Powered Threat Modeling."""

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from aitm.core.config import AITMConfig, ModelProvider
from aitm.core.engine import ThreatModelingEngine
from aitm.export.json_export import export_json
from aitm.export.markdown_export import export_markdown

app = typer.Typer(
    name="aitm",
    help="AI-Powered Threat Modeling — Automated STRIDE analysis for system architectures.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def analyze(
    image: Path = typer.Option(None, "--image", "-i", help="Path to architecture diagram (PNG/JPEG)"),
    description: str = typer.Option(None, "--description", "-d", help="System description"),
    description_file: Path = typer.Option(None, "--description-file", "-f", help="File containing system description"),
    provider: str = typer.Option("bedrock", "--provider", "-p", help="AI provider: bedrock, openai, or ollama"),
    model: str = typer.Option(None, "--model", "-m", help="Model ID (auto-detected if not set)"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("markdown", "--format", help="Output format: markdown, json"),
    reasoning: int = typer.Option(0, "--reasoning", "-r", help="Reasoning level (0=off, 1=low, 2=medium, 3=high)"),
):
    """Analyze a system architecture for security threats using STRIDE methodology."""

    # Validate inputs
    if not description and not description_file:
        console.print("[red]Error:[/red] Provide --description or --description-file")
        raise typer.Exit(1)

    # Load description from file if provided
    if description_file:
        if not description_file.exists():
            console.print(f"[red]Error:[/red] File not found: {description_file}")
            raise typer.Exit(1)
        description = description_file.read_text()

    # Validate image if provided
    if image and not image.exists():
        console.print(f"[red]Error:[/red] Image not found: {image}")
        raise typer.Exit(1)

    # Build config
    try:
        config = AITMConfig(
            provider=ModelProvider(provider),
            model_id=model,
            reasoning_level=reasoning,
        )
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Display header
    console.print(Panel.fit(
        "[bold blue]AI-Powered Threat Modeling[/bold blue]\n"
        f"Provider: {config.provider.value} | Model: {config.get_model_id()}",
        border_style="blue",
    ))

    # Run analysis
    engine = ThreatModelingEngine(config)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing architecture...", total=None)

        result = engine.run(
            description=description,
            image_path=image,
        )

        progress.update(task, description="Analysis complete!")

    # Display summary
    console.print(f"\n[green]✓[/green] Found [bold]{len(result.threats)}[/bold] threats")
    console.print(f"  Assets: {len(result.assets)} | Flows: {len(result.data_flows)}")

    # Threat breakdown by STRIDE
    stride_counts = {}
    for threat in result.threats:
        cat = threat.stride_category.value
        stride_counts[cat] = stride_counts.get(cat, 0) + 1

    if stride_counts:
        console.print("\n  STRIDE breakdown:")
        for cat, count in sorted(stride_counts.items(), key=lambda x: -x[1]):
            console.print(f"    {cat}: {count}")

    # Export
    if format == "json":
        output_content = export_json(result)
        default_ext = ".json"
    else:
        output_content = export_markdown(result)
        default_ext = ".md"

    if output:
        output.write_text(output_content)
        console.print(f"\n[green]✓[/green] Report saved to: {output}")
    else:
        # Auto-generate output filename
        auto_path = Path(f"threat-model{default_ext}")
        auto_path.write_text(output_content)
        console.print(f"\n[green]✓[/green] Report saved to: {auto_path}")


@app.command()
def version():
    """Show AITM version."""
    from aitm import __version__
    console.print(f"aitm v{__version__}")


if __name__ == "__main__":
    app()
