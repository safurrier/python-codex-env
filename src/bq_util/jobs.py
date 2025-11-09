"""Job discovery and analysis helpers for the bq_util CLI."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from importlib import import_module
from typing import Any

from rich.console import Console
from rich.progress import Progress
from rich.table import Table


def list_recent_jobs(
    client: Any, console: Console, max_results: int = 20
) -> list[dict[str, Any]]:
    """Return metadata for recent jobs owned by the current user."""

    jobs: list[dict[str, Any]] = []

    with Progress(console=console, transient=True) as progress:
        task = progress.add_task("[cyan]Fetching recent jobs...", total=None)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        try:
            iterator = client.list_jobs(
                max_results=max_results,
                min_creation_time=seven_days_ago,
                all_users=False,
            )
        except Exception as exc:  # pragma: no cover - dependent on client behaviour
            console.print(f"[yellow]Warning when fetching jobs: {exc}")
            return []

        for job in iterator:
            job_info = {
                "job_id": job.job_id,
                "created": job.created,
                "state": job.state,
                "job_type": job.job_type,
                "display": f"{job.job_type.upper()}: {job.job_id} ({job.state}) - "
                f"{job.created.strftime('%Y-%m-%d %H:%M:%S')}",
            }

            if job.job_type == "query" and getattr(job, "query", None):
                query = job.query.replace("\n", " ")
                preview = query[:50] + ("..." if len(query) > 50 else "")
                job_info["query_preview"] = preview
                job_info["display"] = (
                    f"QUERY: {preview} ({job.state}) - "
                    f"{job.created.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            jobs.append(job_info)

        progress.update(task, completed=100)

    return sorted(jobs, key=lambda entry: entry["created"], reverse=True)


def filter_jobs(jobs: Iterable[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Filter job metadata using a case-insensitive query."""

    if not query:
        return list(jobs)

    pattern = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)
    return [
        job
        for job in jobs
        if pattern.match(job["job_id"]) or pattern.match(job.get("query_preview", ""))
    ]


def interactive_job_selection(console: Console, jobs: list[dict[str, Any]]) -> str:
    """Prompt the user to pick a job from ``jobs`` or enter an id manually."""

    if not jobs:
        raise RuntimeError("No recent jobs found")

    try:
        inquirer = import_module("InquirerPy").inquirer
        choice_module = import_module("InquirerPy.base.control")
        choice_cls = choice_module.Choice
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Interactive job selection requires InquirerPy. Install the optional "
            "'cli' dependency group or provide a job id explicitly."
        ) from exc

    table = Table(title="Recent BigQuery Jobs")
    table.add_column("Job ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("State", style="yellow")
    table.add_column("Created", style="blue")
    table.add_column("Query Preview", style="white")

    for job in jobs[:10]:
        preview = job.get("query_preview", "")
        display_preview = preview[:50] + ("..." if len(preview) > 50 else "")
        job_id = job["job_id"]
        if len(job_id) > 30:
            job_id = job_id[:27] + "..."
        table.add_row(
            job_id,
            job["job_type"].upper(),
            job["state"],
            job["created"].strftime("%Y-%m-%d %H:%M:%S"),
            display_preview,
        )

    console.print(table)

    choices = [
        choice_cls(
            value=job["job_id"],
            name=job.get("display", job["job_id"]),
        )
        for job in jobs
    ]
    choices.append(choice_cls(value="manual", name="Enter job ID manually"))

    selected = inquirer.select(  # pragma: no cover - requires interactive terminal
        message="Select a job to analyse:",
        choices=choices,
        default=choices[0].value if choices else None,
    ).execute()

    if selected == "manual":  # pragma: no cover - interactive path
        return str(inquirer.text(message="Enter job ID:").execute())
    return str(selected)


def analyze_query_plan(job: Any) -> dict[str, Any]:
    """Derive key insights from a BigQuery query plan."""

    plan = getattr(job, "query_plan", None)
    if not plan:
        return {}

    steps = [step for step in plan if getattr(step, "slot_ms", None)]
    sorted_by_time = sorted(steps, key=lambda step: step.slot_ms or 0, reverse=True)
    sorted_by_records = sorted(
        [step for step in plan if getattr(step, "records_read", None)],
        key=lambda step: step.records_read or 0,
        reverse=True,
    )
    sorted_by_shuffle = sorted(
        [step for step in plan if getattr(step, "shuffle_output_bytes", None)],
        key=lambda step: step.shuffle_output_bytes or 0,
        reverse=True,
    )

    bottlenecks: list[dict[str, Any]] = []
    total_slot_ms = getattr(job, "slot_millis", 0) or 0

    if total_slot_ms and sorted_by_time:
        for step in sorted_by_time[:3]:
            pct = (step.slot_ms / total_slot_ms) * 100 if step.slot_ms else 0
            if pct > 25:
                bottlenecks.append(
                    {
                        "type": "time",
                        "step_id": step.entry_id,
                        "name": step.name,
                        "percentage": pct,
                    }
                )

    if sorted_by_records:
        for step in sorted_by_records[:2]:
            bottlenecks.append(
                {
                    "type": "data",
                    "step_id": step.entry_id,
                    "name": step.name,
                    "records": step.records_read,
                }
            )

    if sorted_by_shuffle:
        for step in sorted_by_shuffle[:2]:
            bottlenecks.append(
                {
                    "type": "shuffle",
                    "step_id": step.entry_id,
                    "name": step.name,
                    "bytes": step.shuffle_output_bytes,
                }
            )

    return {
        "steps_count": len(plan),
        "bottlenecks": bottlenecks,
        "top_time_steps": sorted_by_time[:3],
        "top_data_steps": sorted_by_records[:3],
        "top_shuffle_steps": sorted_by_shuffle[:3],
    }


def map_sql_to_steps(query: str, plan: Iterable[Any]) -> list[dict[str, Any]]:
    """Approximate mapping between SQL fragments and plan steps."""

    if not query or not plan:
        return []

    operations_map = {
        "read": ["FROM", "TABLE"],
        "filter": ["WHERE", "HAVING"],
        "aggregate": ["GROUP BY", "COUNT", "SUM", "AVG", "MIN", "MAX"],
        "join": ["JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
        "sort": ["ORDER BY"],
        "window": ["OVER", "PARTITION BY"],
        "compute": ["SELECT", "CASE", "WHEN"],
        "limit": ["LIMIT"],
        "union": ["UNION"],
        "intersect": ["INTERSECT"],
        "except": ["EXCEPT"],
    }

    query_lines = [line.strip() for line in query.splitlines() if line.strip()]
    mappings: list[dict[str, Any]] = []

    for step in plan:
        step_name = getattr(step, "name", "").lower()
        matched_keywords: list[str] = []

        for operation, keywords in operations_map.items():
            if operation in step_name:
                matched_keywords.extend(keywords)

        if not matched_keywords and "input" in step_name:
            matched_keywords = ["FROM", "TABLE"]
        elif not matched_keywords and "output" in step_name:
            matched_keywords = ["SELECT", "INTO"]

        matching_lines = []
        for line_number, line in enumerate(query_lines):
            for keyword in matched_keywords:
                pattern = re.compile(rf"\\b{re.escape(keyword)}\\b", re.IGNORECASE)
                if pattern.search(line):
                    matching_lines.append((line_number, line))
                    break

        if matching_lines:
            mappings.append(
                {
                    "step_id": getattr(step, "entry_id", None),
                    "step_name": getattr(step, "name", ""),
                    "matching_lines": matching_lines,
                }
            )

    return mappings
