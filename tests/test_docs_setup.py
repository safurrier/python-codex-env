"""Test MkDocs documentation setup and configuration."""

from __future__ import annotations

from pathlib import Path

import tomli


def test_mkdocs_dependencies_configured() -> None:
    """Test that MkDocs dependencies are configured in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml should exist"

    with pyproject_path.open("rb") as handle:
        config = tomli.load(handle)

    if "dependency-groups" in config and "dev" in config["dependency-groups"]:
        dev_deps = config["dependency-groups"]["dev"]

        mkdocs_deps = [dep for dep in dev_deps if "mkdocs" in dep.lower()]

        if mkdocs_deps:
            assert len(mkdocs_deps) >= 2, (
                "Should have mkdocs-material and mkdocstrings dependencies"
            )

            has_material = any("mkdocs-material" in dep for dep in dev_deps)
            has_mkdocstrings = any("mkdocstrings" in dep for dep in dev_deps)

            assert has_material, "Should have mkdocs-material dependency"
            assert has_mkdocstrings, "Should have mkdocstrings dependency"


def test_mkdocs_config_exists() -> None:
    """Test that mkdocs.yml configuration file exists (if docs enabled)."""
    mkdocs_config = Path("mkdocs.yml")
    if mkdocs_config.exists():
        assert mkdocs_config.is_file(), "mkdocs.yml should be a file"


def test_mkdocs_config_valid() -> None:
    """Test that mkdocs.yml has valid configuration (if it exists)."""
    mkdocs_config = Path("mkdocs.yml")
    if not mkdocs_config.exists():
        return

    import yaml

    with mkdocs_config.open("r", encoding="utf8") as handle:
        config = yaml.safe_load(handle)

    assert "site_name" in config, "mkdocs.yml should have site_name"
    assert "theme" in config, "mkdocs.yml should have theme configuration"
    assert config["theme"]["name"] == "material", "Should use Material theme"
    assert "plugins" in config, "mkdocs.yml should have plugins"

    plugin_names = []
    for plugin in config["plugins"]:
        if isinstance(plugin, dict):
            plugin_names.extend(plugin.keys())
        else:
            plugin_names.append(plugin)

    assert "search" in plugin_names, "Should have search plugin"
    assert "mkdocstrings" in plugin_names, "Should have mkdocstrings plugin"


def test_documentation_structure_exists() -> None:
    """Test that basic documentation structure exists (if docs enabled)."""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        return

    assert docs_dir.is_dir(), "docs should be a directory"

    index_file = docs_dir / "index.md"
    assert index_file.exists(), "docs/index.md should exist"


def test_makefile_has_docs_targets() -> None:
    """Test that Makefile contains documentation targets."""
    makefile_path = Path("Makefile")
    assert makefile_path.exists(), "Makefile should exist"

    with makefile_path.open("r", encoding="utf8") as handle:
        makefile_content = handle.read()

    assert "docs-install:" in makefile_content, (
        "Makefile should have docs-install target"
    )
    assert "docs-build:" in makefile_content, "Makefile should have docs-build target"
    assert "docs-serve:" in makefile_content, "Makefile should have docs-serve target"
    assert "docs-check:" in makefile_content, "Makefile should have docs-check target"
    assert "docs-clean:" in makefile_content, "Makefile should have docs-clean target"


def test_github_actions_docs_workflow() -> None:
    """Test that GitHub Actions workflow for docs exists (if docs enabled)."""
    workflow_path = Path(".github/workflows/docs.yml")
    if not workflow_path.exists():
        return

    import yaml

    with workflow_path.open("r", encoding="utf8") as handle:
        workflow = yaml.safe_load(handle)

    assert True in workflow or "on" in workflow, (
        "Workflow should have trigger configuration"
    )
    assert "jobs" in workflow, "Workflow should have jobs"

    jobs = workflow["jobs"]
    assert any(
        "deploy" in job_name.lower() or "docs" in job_name.lower()
        for job_name in jobs.keys()
    ), "Should have a docs deployment job"


def test_template_files_exist() -> None:
    """Test that template files exist for documentation setup."""
    template_dir = Path("templates")
    assert template_dir.exists(), "templates/ directory should exist"

    template_files = [
        "mkdocs.yml.template",
        "docs/index.md.template",
        "docs/getting-started.md.template",
        "docs/reference/api.md.template",
        ".github/workflows/docs.yml.template",
    ]

    for template_file in template_files:
        template_path = template_dir / template_file
        assert template_path.exists(), f"Template file {template_file} should exist"
