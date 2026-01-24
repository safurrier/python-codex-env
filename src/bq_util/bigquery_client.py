"""Helpers for accessing the Google BigQuery client library."""

from __future__ import annotations

from typing import Any


class BigQueryDependencyError(RuntimeError):
    """Raised when the BigQuery client library is not available."""


def get_bigquery_client(
    project: str | None = None,
) -> Any:  # pragma: no cover - thin wrapper
    """Return a :class:`google.cloud.bigquery.Client` instance.

    The import is performed lazily so that unit tests can run without the
    optional Google Cloud dependencies installed.
    """

    try:
        from google.cloud import bigquery  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised via CLI error handling
        raise BigQueryDependencyError(
            "google-cloud-bigquery is required for this command. "
            "Install the optional 'cli' dependency group to enable BigQuery "
            "features."
        ) from exc

    return bigquery.Client(project=project)
