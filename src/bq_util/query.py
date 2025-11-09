"""Query execution utilities for the bq_util CLI."""

from __future__ import annotations

import re
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from .bigquery_client import BigQueryDependencyError, get_bigquery_client

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from rich.table import Table


def format_bytes(bytes_value: int | None) -> str:
    """Return a human-readable byte representation."""

    if not bytes_value:
        return "0 B"

    value = float(bytes_value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} PB"


def format_duration(
    start_time: datetime | None,
    end_time: datetime | None,
    milliseconds: int | None = None,
) -> str:
    """Convert a duration into a human-friendly string."""

    if milliseconds is not None:
        duration = milliseconds / 1000.0
    elif start_time is None or end_time is None:
        return "Running..."
    else:
        duration = (end_time - start_time).total_seconds()

    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"
    if minutes > 0:
        return f"{int(minutes)}m {seconds:.2f}s"
    return f"{seconds:.2f}s"


def extract_table_references(query: str) -> list[str]:
    """Return table references found in ``query``."""

    pattern = r"FROM\s+[`]?{{?\s*ref\(['\"]([\w_]+)['\"](?:,\s*['\"][\w_]+['\"])?\s*\)}\}?[`]?"
    tables = re.findall(pattern, query, re.IGNORECASE)
    pattern_direct = r"FROM\s+[`]?([\w\._]+)[`]?"
    tables.extend(re.findall(pattern_direct, query, re.IGNORECASE))
    return tables


def replace_dbt_refs(query: str, project: str) -> str:
    """Replace ``dbt`` ``ref`` macros with fully qualified table names."""

    pattern = r"{{[\s]*ref\(['\"](\w+)['\"](?:,[\s]*['\"](\w+)['\"])?[\s]*\)[\s]*}}"

    def _replace(match: re.Match[str]) -> str:
        table = match.group(1)
        if match.group(2):
            table = match.group(2)
        return f"`{project}.dbt_testing.{table}`"

    modified_query = re.sub(pattern, _replace, query)

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    modified_query = modified_query.replace(
        "{{ start_date() }}", f"'{yesterday} 00:00:00'"
    )
    modified_query = modified_query.replace("{{ end_date() }}", f"'{today} 00:00:00'")

    return modified_query


def run_query(
    query: str, project: str
) -> tuple[Any, float]:  # pragma: no cover - integration path
    """Execute ``query`` against BigQuery returning the job and execution time."""

    try:
        client = get_bigquery_client(project=project)
    except BigQueryDependencyError as exc:  # pragma: no cover - CLI error surface
        raise RuntimeError(str(exc)) from exc

    start = time.time()
    job = client.query(query)
    job.result()
    execution_time = time.time() - start
    return job, execution_time


def format_query_stats(job: Any, execution_time: float) -> Table:
    """Create a rich table describing query statistics."""

    from rich.table import Table

    stats_table = Table(title="Query Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")

    bytes_processed = getattr(job, "total_bytes_processed", 0) or 0
    stats_table.add_row("Execution Time", f"{execution_time:.2f} seconds")
    stats_table.add_row(
        "Bytes Processed",
        f"{bytes_processed:,} bytes ({bytes_processed / 1073741824 if bytes_processed else 0:.2f} GB)",
    )

    bytes_billed = getattr(job, "total_bytes_billed", 0) or 0
    stats_table.add_row(
        "Bytes Billed",
        f"{bytes_billed:,} bytes ({bytes_billed / 1073741824 if bytes_billed else 0:.2f} GB)",
    )

    slot_millis = getattr(job, "slot_millis", 0) or 0
    stats_table.add_row(
        "Slot Time", f"{slot_millis / 1000 if slot_millis else 0:.2f} seconds"
    )

    referenced_tables = getattr(job, "referenced_tables", None)
    if referenced_tables:
        table_lines = []
        for table in referenced_tables:
            if hasattr(table, "project") and hasattr(table, "dataset_id"):
                table_lines.append(
                    f"{table.project}.{table.dataset_id}.{table.table_id}"
                )
            else:
                table_lines.append(str(table))
        stats_table.add_row("Referenced Tables", "\n".join(table_lines))

    return stats_table


def get_query_results_preview(job: Any, max_rows: int = 5) -> Table:
    """Return a preview of query results as a rich table."""

    from rich.table import Table

    dataframe = job.to_dataframe().head(max_rows)

    preview_table = Table(
        title=f"Results Preview (first {min(max_rows, len(dataframe))} rows)"
    )
    for column in dataframe.columns:
        preview_table.add_column(str(column))

    for _, row in dataframe.iterrows():
        values = [str(value) for value in row]
        preview_table.add_row(*values)

    return preview_table
