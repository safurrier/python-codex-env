from pathlib import Path

import yaml

from src.pi_docs_bot.command import parse_comment
from src.pi_docs_bot.config import load_config
from src.pi_docs_bot.models import CommentCommand, Mode, PiDocsConfig, Scope
from src.pi_docs_bot.policy import (
    allowed_paths_for_scope,
    check_diff_limits,
    check_path_policy,
    resolve_settings,
)
from src.pi_docs_bot.validation import build_validation_plan, detect_doc_systems


def test_parse_comment_defaults():
    result = parse_comment("/pi docs")
    assert result.command is not None
    assert result.command.scope is None
    assert result.errors == ()


def test_parse_comment_with_options():
    result = parse_comment(
        "/pi docs scope=readme validate=false mode=stacked "
        "paths=docs,README.md max_files=10 max_diff_lines=120"
    )
    assert result.errors == ()
    assert result.command == CommentCommand(
        scope=Scope.README,
        validate=False,
        mode=Mode.STACKED,
        paths=("docs", "README.md"),
        max_files=10,
        max_diff_lines=120,
        free_text="",
    )


def test_parse_comment_invalid_values():
    result = parse_comment("/pi docs scope=unknown validate=maybe max_files=0")
    assert result.command is None
    assert "Invalid scope: unknown" in result.errors
    assert "Invalid validate: maybe" in result.errors
    assert "max_files must be positive" in result.errors


def test_load_config_from_yaml(tmp_path):
    config_path = tmp_path / ".pi-docs.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "allowed_paths": ["docs/**", "README.md"],
                "doc_build_command": "mkdocs build",
                "default_scope": "readme",
                "max_files": 10,
                "deny_patterns": ["**/*.key"],
            }
        ),
        encoding="utf-8",
    )
    config = load_config(config_path)
    assert config.allowed_paths == ("docs/**", "README.md")
    assert config.doc_build_command == "mkdocs build"
    assert config.default_scope == Scope.README
    assert config.max_files == 10
    assert config.deny_patterns == ("**/*.key",)


def test_resolve_settings_prefers_command_over_config():
    command = CommentCommand(scope=Scope.ALL, max_files=5)
    config = PiDocsConfig(default_scope=Scope.README, max_files=50)
    settings = resolve_settings(command, config)
    assert settings.scope == Scope.ALL
    assert settings.max_files == 5
    assert settings.allowed_paths == allowed_paths_for_scope(Scope.ALL)


def test_check_path_policy_respects_allowlist_and_denies():
    result = check_path_policy(
        ["docs/index.md", "src/app.py", "secrets.env"],
        allowed_paths=("docs/**",),
        deny_patterns=("**/*.env",),
    )
    assert result.allowed is False
    assert "Not in allowlist: src/app.py" in result.violations
    assert "Denied path: secrets.env" in result.violations


def test_check_diff_limits():
    result = check_diff_limits(5, 201, max_files=4, max_diff_lines=200)
    assert result.allowed is False
    assert "Changed files (5) exceed max_files (4)" in result.violations
    assert "Diff lines (201) exceed max_diff_lines (200)" in result.violations


def test_detect_doc_systems_and_validation_plan(tmp_path):
    (tmp_path / "mkdocs.yml").write_text("site_name: test", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "package.json").write_text(
        '{"scripts": {"docs:build": "docusaurus build"}}', encoding="utf-8"
    )
    config = PiDocsConfig()
    info = detect_doc_systems(tmp_path, config)
    assert "mkdocs" in info.systems
    assert "docusaurus" in info.systems
    assert info.build_command is not None
    plan = build_validation_plan(tmp_path, config)
    assert plan.build_command == info.build_command


def test_detect_doc_systems_none(tmp_path):
    config = PiDocsConfig()
    info = detect_doc_systems(tmp_path, config)
    assert info.systems == ()
    assert "No doc system detected" in info.notes
