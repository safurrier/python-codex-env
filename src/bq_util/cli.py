"""Command line interface for the bq-util BigQuery helper."""

from __future__ import annotations

import json
from importlib import import_module
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Any, cast

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .bigquery_client import BigQueryDependencyError, get_bigquery_client
from .config import Config, get_config_path
from .config import load_config as _load_config
from .config import save_config as _save_config
from .jobs import (
    analyze_query_plan,
    interactive_job_selection,
    list_recent_jobs,
    map_sql_to_steps,
)
from .projects import filter_projects, interactive_project_selection, list_projects
from .query import (
    format_bytes,
    format_duration,
    format_query_stats,
    get_query_results_preview,
    replace_dbt_refs,
    run_query,
)

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from rich.progress import Progress, TaskID


console = Console()


def get_config() -> Config:
    """Wrapper to load the persisted configuration."""

    return _load_config()


def save_config(config: Config) -> None:
    """Persist configuration changes."""

    _save_config(config)


def _load_inquirer() -> Any:
    return import_module("InquirerPy").inquirer


def _prompt_to_save_default(project_id: str, config: Config) -> None:
    try:
        inquirer = _load_inquirer()
    except ModuleNotFoundError:
        return

    if inquirer.confirm(
        message=f"Do you want to save {project_id} as your default project?",
        default=True,
    ).execute():
        config.default_project = project_id
        save_config(config)
        console.print(f"[green]Saved {project_id} as your default project[/green]")


def get_project(project_option: str | None = None) -> str:
    """Determine which project should be used for a command."""

    if project_option:
        return project_option

    config = get_config()
    if config.default_project:
        console.print(
            f"[green]Using default project from config: {config.default_project}[/green]"
        )
        return config.default_project

    projects = list_projects(console)
    if len(projects) == 1:
        project_id = projects[0]
        _prompt_to_save_default(project_id, config)
        return project_id
    if len(projects) > 1:
        try:
            inquirer = _load_inquirer()
        except ModuleNotFoundError:
            return projects[0]

        selected_projects = projects
        if len(projects) > 25:
            if inquirer.confirm(
                message="Search for a specific project?",
                default=True,
            ).execute():
                query = inquirer.text(message="Enter search term:").execute()
                filtered = filter_projects(projects, query)
                if filtered:
                    console.print(
                        f"[green]Found {len(filtered)} matching projects.[/green]"
                    )
                    selected_projects = filtered
                else:
                    console.print(
                        "[yellow]No projects matched your search. Showing all projects.[/yellow]"
                    )

        project_id = interactive_project_selection(console, selected_projects)
        return str(project_id)

    console.print(
        "[yellow]No projects found. Please enter a project ID manually.[/yellow]"
    )
    return cast(str, click.prompt("Enter Google Cloud project ID", type=str))


@click.group()
def cli() -> None:
    """BigQuery Analysis Tool."""


@cli.command("config")
@click.option("--set-project", "set_project", help="Set default project ID")
@click.option("--show", is_flag=True, help="Show current configuration")
@click.option("--reset", is_flag=True, help="Reset configuration to defaults")
def configure(
    set_project: str | None = None, show: bool = False, reset: bool = False
) -> None:
    """Manage persistent configuration for the CLI."""

    config = get_config()
    config_path = get_config_path()
    if not config_path.exists():
        save_config(config)

    if reset:
        config = Config()
        save_config(config)
        console.print("[green]Configuration reset to defaults[/green]")

    if set_project:
        config.default_project = set_project
        save_config(config)
        console.print(f"[green]Default project set to: {set_project}[/green]")

    if show or (not set_project and not reset):
        console.print("[bold]Current Configuration:[/bold]")
        table = Table()
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Default Project", config.default_project or "[dim]Not set[/dim]")
        table.add_row("Config File", str(get_config_path()))
        console.print(table)


class ProgressContext:
    """Context manager to wrap operations with a transient progress bar."""

    def __init__(
        self, console: Console, message: str = "[cyan]Fetching job..."
    ) -> None:
        self._console = console
        self._message = message
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None

    def __enter__(self) -> Progress:
        from rich.progress import Progress

        self._progress = Progress(console=self._console, transient=True)
        progress = self._progress.__enter__()
        self._task_id = self._progress.add_task(self._message, total=None)
        return progress

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._progress and self._task_id is not None:
            self._progress.update(self._task_id, completed=100)
            self._task_id = None
        if self._progress:
            self._progress.__exit__(exc_type, exc, tb)
            self._progress = None


@cli.command("analyze")
@click.argument("job_id", required=False)
@click.option("--project", "project", help="Google Cloud project ID")
@click.option("--format", "format", type=click.Choice(["text", "json"]), default="text")
@click.option("--verbose", "verbose", is_flag=True, help="Show verbose output")
@click.option(
    "--llm", "llm", is_flag=True, help="Format output specifically for LLM optimisation"
)
@click.option(
    "--debug", "debug", is_flag=True, help="Show debug information about job object"
)
@click.option(
    "--last", "last", is_flag=True, help="Analyse the most recently executed query job"
)
def analyze_job(
    job_id: str | None = None,
    project: str | None = None,
    format: str = "text",
    verbose: bool = False,
    llm: bool = False,
    debug: bool = False,
    last: bool = False,
) -> None:
    """Analyse a BigQuery job and display execution insights."""

    if last:
        config = get_config()
        if config.last_job_id and config.last_job_project:
            job_id = config.last_job_id
            project = config.last_job_project
            console.print(
                f"[green]Using last job: {job_id} from project: {project}[/green]"
            )
        else:
            console.print(
                "[yellow]No recent job found in history. Please specify a job ID.[/yellow]"
            )
            return

    elif job_id and ":" in job_id and not project:
        project, job_id = job_id.split(":", 1)
    elif job_id and not project:
        project = get_project()
    elif project and not job_id:
        try:
            client = get_bigquery_client(project=project)
        except BigQueryDependencyError as exc:
            raise click.ClickException(str(exc)) from exc
        jobs = list_recent_jobs(client, console)
        job_id = interactive_job_selection(console, jobs)
    elif not job_id and not project:
        project = get_project()
        try:
            client = get_bigquery_client(project=project)
        except BigQueryDependencyError as exc:
            raise click.ClickException(str(exc)) from exc
        jobs = list_recent_jobs(client, console)
        job_id = interactive_job_selection(console, jobs)

    if not project or not job_id:
        raise click.ClickException("A project and job id are required for analysis")

    try:
        client = get_bigquery_client(project=project)
    except BigQueryDependencyError as exc:
        raise click.ClickException(str(exc)) from exc

    with ProgressContext(console, message=f"[cyan]Fetching job {job_id}..."):
        job = client.get_job(job_id, project=project)

    if debug:
        console.print("\n[bold]Debug Information:[/bold]")
        console.print("[bold]Job Attributes:[/bold]")
        for attr in dir(job):
            if not attr.startswith("_"):
                try:
                    value = getattr(job, attr)
                except Exception as exc:  # pragma: no cover - diagnostic path
                    console.print(f"- {attr}: Error accessing: {exc}")
                else:
                    console.print(f"- {attr}: {type(value)}")

    job_info = {
        "job_id": job.job_id,
        "project": job.project,
        "location": job.location,
        "created": job.created.isoformat() if getattr(job, "created", None) else None,
        "state": job.state,
        "error_result": job.error_result,
        "user_email": getattr(job, "user_email", None),
        "job_type": job.job_type,
    }

    if getattr(job, "started", None):
        job_info["started"] = job.started.isoformat()
        if getattr(job, "ended", None):
            job_info["ended"] = job.ended.isoformat()
            job_info["duration"] = format_duration(job.started, job.ended)

    if job.job_type == "query":
        query_info: dict[str, Any] = {
            "query": job.query,
            "bytes_processed": job.total_bytes_processed,
            "bytes_processed_formatted": format_bytes(job.total_bytes_processed),
            "slot_ms": job.slot_millis,
            "billing_tier": getattr(job, "billing_tier", None),
            "cache_hit": job.cache_hit,
        }

        if getattr(job, "destination", None):
            destination = job.destination
            if hasattr(destination, "project"):
                query_info["destination_table"] = {
                    "project": destination.project,
                    "dataset": destination.dataset_id,
                    "table": destination.table_id,
                }
            else:
                query_info["destination_table"] = str(destination)

        if job.state == "DONE":
            if getattr(job, "query_plan", None):
                query_info["query_plan"] = []
                for step in job.query_plan:
                    query_info["query_plan"].append(
                        {
                            "name": step.name,
                            "entry_id": step.entry_id,
                            "input_stages": step.input_stages,
                            "start": getattr(step, "start", None),
                            "end": getattr(step, "end", None),
                            "records_read": getattr(step, "records_read", None),
                            "records_written": getattr(step, "records_written", None),
                            "status": getattr(step, "status", None),
                            "shuffle_output_bytes": getattr(
                                step, "shuffle_output_bytes", None
                            ),
                            "slot_ms": getattr(step, "slot_ms", None),
                            "compute_ms_avg": getattr(step, "compute_ms_avg", None),
                            "compute_ms_max": getattr(step, "compute_ms_max", None),
                            "wait_ms_avg": getattr(step, "wait_ms_avg", None),
                            "wait_ms_max": getattr(step, "wait_ms_max", None),
                        }
                    )

                query_info["query_plan_analysis"] = analyze_query_plan(job)
                if job.query:
                    query_info["sql_mapping"] = map_sql_to_steps(
                        job.query, job.query_plan
                    )
            else:
                query_info["query_plan"] = []

            query_info["referenced_tables"] = [
                str(table) for table in getattr(job, "referenced_tables", [])
            ]

        job_info["query_details"] = query_info

    if llm:
        llm_output: dict[str, Any] = {
            "query": job.query if job.job_type == "query" else "",
            "performance_data": {
                "bytes_processed": job.total_bytes_processed
                if job.job_type == "query"
                else 0,
                "bytes_processed_human": format_bytes(job.total_bytes_processed),
                "slot_milliseconds": job.slot_millis if job.job_type == "query" else 0,
                "duration_seconds": (job.ended - job.started).total_seconds()
                if getattr(job, "started", None) and getattr(job, "ended", None)
                else 0,
                "cache_hit": job.cache_hit if job.job_type == "query" else False,
            },
        }

        if job.job_type == "query" and getattr(job, "query_plan", None):
            analysis = analyze_query_plan(job)
            if analysis.get("top_time_steps"):
                llm_output["top_time_consuming_steps"] = [
                    {
                        "step_id": step.entry_id,
                        "name": step.name,
                        "slot_ms": step.slot_ms,
                        "percentage_of_total": (step.slot_ms / job.slot_millis) * 100
                        if job.slot_millis
                        else 0,
                    }
                    for step in analysis["top_time_steps"]
                ]

            if analysis.get("top_data_steps"):
                llm_output["top_data_processing_steps"] = [
                    {
                        "step_id": step.entry_id,
                        "name": step.name,
                        "records_read": step.records_read,
                        "records_written": getattr(step, "records_written", None),
                    }
                    for step in analysis["top_data_steps"]
                ]

            if analysis.get("bottlenecks"):
                llm_output["bottlenecks"] = analysis["bottlenecks"]

        click.echo(json.dumps(llm_output, indent=2))
        return

    if format == "json":
        click.echo(json.dumps(job_info, indent=2))
        return

    console.print(Panel.fit(f"[bold]BigQuery Job: {job.job_id}[/bold]"))
    console.print(f"[bold]Status:[/bold] {job.state}")
    console.print(f"[bold]Type:[/bold] {job.job_type}")
    console.print(f"[bold]User:[/bold] {getattr(job, 'user_email', 'Unknown')}")
    console.print(f"[bold]Created:[/bold] {job.created.isoformat()}")

    if getattr(job, "started", None):
        console.print(f"[bold]Started:[/bold] {job.started.isoformat()}")
        if getattr(job, "ended", None):
            console.print(f"[bold]Ended:[/bold] {job.ended.isoformat()}")
            console.print(
                f"[bold]Duration:[/bold] {format_duration(job.started, job.ended)}"
            )

    if job.error_result:
        console.print("[bold red]Error:[/bold red]", job.error_result)
        console.print(
            "[bold red]No query plan or execution details will be present in this report[/bold red]"
        )

    if job.job_type == "query":
        console.print("\n[bold]Query Details:[/bold]")
        console.print(f"[bold]Query:[/bold]\n{job.query}")

        if job.total_bytes_processed:
            console.print(
                f"[bold]Bytes Processed:[/bold] {format_bytes(job.total_bytes_processed)}"
            )

        console.print(f"[bold]Cache Hit:[/bold] {job.cache_hit}")

        if getattr(job, "query_plan", None):
            console.print("\n[bold]Query Plan:[/bold]")
            plan_table = Table(title="Query Execution Plan - Performance Analysis")
            plan_table.add_column("ID", style="cyan", width=5)
            plan_table.add_column("Name", style="green")
            plan_table.add_column("Records\nRead", style="blue", justify="right")
            plan_table.add_column("Records\nWritten", style="magenta", justify="right")
            plan_table.add_column("Shuffle\nBytes", style="yellow", justify="right")
            plan_table.add_column("Slot MS", style="white", justify="right")

            if verbose:
                plan_table.add_column("Wait\nMS Avg", style="red", justify="right")
                plan_table.add_column("Compute\nMS Avg", style="green", justify="right")

            max_slot_ms = max((step.slot_ms or 0) for step in job.query_plan)
            max_records_read = max((step.records_read or 0) for step in job.query_plan)
            max_shuffle = max(
                (getattr(step, "shuffle_output_bytes", 0) or 0)
                for step in job.query_plan
            )

            for step in job.query_plan:
                records_read = (
                    f"{step.records_read:,}"
                    if getattr(step, "records_read", None)
                    else "-"
                )
                records_written = (
                    f"{step.records_written:,}"
                    if getattr(step, "records_written", None)
                    else "-"
                )
                shuffle_bytes = (
                    format_bytes(step.shuffle_output_bytes)
                    if getattr(step, "shuffle_output_bytes", None)
                    else "-"
                )
                slot_ms = f"{step.slot_ms:,}" if getattr(step, "slot_ms", None) else "-"

                slot_style = (
                    "bold red"
                    if getattr(step, "slot_ms", 0) and step.slot_ms > max_slot_ms * 0.7
                    else "white"
                )
                read_style = (
                    "bold blue"
                    if getattr(step, "records_read", 0)
                    and step.records_read > max_records_read * 0.7
                    else "blue"
                )
                shuffle_style = (
                    "bold yellow"
                    if getattr(step, "shuffle_output_bytes", 0)
                    and step.shuffle_output_bytes > max_shuffle * 0.7
                    else "yellow"
                )

                if verbose:
                    wait_ms = (
                        f"{step.wait_ms_avg:,.1f}"
                        if getattr(step, "wait_ms_avg", None)
                        else "-"
                    )
                    compute_ms = (
                        f"{step.compute_ms_avg:,.1f}"
                        if getattr(step, "compute_ms_avg", None)
                        else "-"
                    )
                    plan_table.add_row(
                        str(step.entry_id),
                        step.name,
                        f"[{read_style}]{records_read}[/{read_style}]",
                        records_written,
                        f"[{shuffle_style}]{shuffle_bytes}[/{shuffle_style}]",
                        f"[{slot_style}]{slot_ms}[/{slot_style}]",
                        wait_ms,
                        compute_ms,
                    )
                else:
                    plan_table.add_row(
                        str(step.entry_id),
                        step.name,
                        f"[{read_style}]{records_read}[/{read_style}]",
                        records_written,
                        f"[{shuffle_style}]{shuffle_bytes}[/{shuffle_style}]",
                        f"[{slot_style}]{slot_ms}[/{slot_style}]",
                    )

            console.print(plan_table)

            console.print("\n[bold]Performance Insights:[/bold]")
            top_steps_by_time = sorted(
                [step for step in job.query_plan if getattr(step, "slot_ms", None)],
                key=lambda step: step.slot_ms or 0,
                reverse=True,
            )[:3]

            if top_steps_by_time:
                console.print("[bold]Top Time-Consuming Steps:[/bold]")
                for step in top_steps_by_time:
                    pct = (
                        (step.slot_ms / job.slot_millis) * 100 if job.slot_millis else 0
                    )
                    console.print(
                        f"  Step {step.entry_id}: {step.name} - {format_duration(None, None, milliseconds=step.slot_ms)} "
                        f"({pct:.1f}% of total)"
                    )

            top_steps_by_data = sorted(
                [
                    step
                    for step in job.query_plan
                    if getattr(step, "records_read", None)
                ],
                key=lambda step: step.records_read or 0,
                reverse=True,
            )[:3]

            if top_steps_by_data:
                console.print("[bold]Top Data-Processing Steps:[/bold]")
                for step in top_steps_by_data:
                    console.print(
                        f"  Step {step.entry_id}: {step.name} - {step.records_read:,} records read"
                    )

            if verbose and job.query:
                sql_mapping = map_sql_to_steps(job.query, job.query_plan)
                if sql_mapping:
                    console.print(
                        "\n[bold]Query Plan to SQL Mapping (Approximate):[/bold]"
                    )
                    console.print(
                        "[yellow]Note: This is a best-effort mapping and may not be fully accurate[/yellow]"
                    )
                    for mapping in sql_mapping:
                        console.print(
                            f"[bold]Step {mapping['step_id']} ({mapping['step_name']})[/bold] may relate to:"
                        )
                        for line_num, line in mapping["matching_lines"]:
                            console.print(
                                f"  Line {line_num + 1}: [green]{line}[/green]"
                            )


@cli.command("query")
@click.argument("query_file", type=click.Path(exists=True, readable=True))
@click.option("--project", "project", help="Google Cloud project ID")
@click.option(
    "--analyze", "analyze", is_flag=True, help="Run analyze command on the query job"
)
@click.option("--verbose", "verbose", is_flag=True, help="Show verbose output")
@click.option(
    "--output", "output", type=click.Path(), help="Save query results to a file"
)
@click.option(
    "--preview-rows",
    "preview_rows",
    type=int,
    default=5,
    help="Number of rows to preview",
)
@click.option(
    "--set-default-project",
    "set_default_project",
    is_flag=True,
    help="Set the project as default",
)
def execute_query(
    query_file: str,
    project: str | None = None,
    analyze: bool = False,
    verbose: bool = False,
    output: str | None = None,
    preview_rows: int = 5,
    set_default_project: bool = False,
) -> None:
    """Execute a SQL query from ``query_file`` against BigQuery."""

    query_path = Path(query_file)

    try:
        query = query_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise click.ClickException(f"Unable to read file: {exc}") from exc

    console.print(Panel(f"Processing query from {query_file}", style="cyan"))

    project = get_project(project)

    if set_default_project:
        config = get_config()
        config.default_project = project
        save_config(config)
        console.print(f"[green]Saved {project} as your default project[/green]")

    processed_query = replace_dbt_refs(query, project) if "{{ ref(" in query else query

    if verbose:
        console.print(Panel(processed_query, title="Processed Query", style="dim"))

    try:
        job, execution_time = run_query(processed_query, project)
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(
        f"[green]Query completed successfully in {execution_time:.2f} seconds![/green]"
    )

    config = get_config()
    config.last_job_id = job.job_id
    config.last_job_project = project
    save_config(config)

    console.print(format_query_stats(job, execution_time))
    console.print(get_query_results_preview(job, max_rows=preview_rows))

    if output:
        from rich.progress import Progress

        dataframe = job.to_dataframe()
        with Progress(console=console, transient=True) as progress:
            task = progress.add_task("[cyan]Saving results...", total=None)
            saved_path = _write_dataframe(dataframe, output)
            progress.update(task, completed=100)
        console.print(f"[green]Results saved to {saved_path}[/green]")

    console.print(f"\n[dim]Job ID: {job.job_id}[/dim]")

    if analyze:
        console.print("\n[cyan]Running detailed analysis on the query job...[/cyan]")
        analyze_job(job.job_id, project, verbose=verbose)
    else:
        console.print("[dim]To analyse this query, run either:[/dim]")
        console.print(f"[cyan]bq-util analyze {job.job_id} --project {project}[/cyan]")
        console.print("[dim]Or simply use:[/dim]")
        console.print("[cyan]bq-util analyze --last[/cyan]")


def _write_dataframe(dataframe: Any, output: str) -> Path:
    path = Path(output)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        dataframe.to_csv(path, index=False)
    elif suffix == ".json":
        dataframe.to_json(path, orient="records", lines=True)
    elif suffix == ".parquet":
        dataframe.to_parquet(path, index=False)
    else:
        path = path.with_suffix(".csv")
        dataframe.to_csv(path, index=False)

    return path


def main() -> None:  # pragma: no cover - entry point helper
    cli()
