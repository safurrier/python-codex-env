from __future__ import annotations

from click.testing import CliRunner

from dread.cli import cli


class StubClient:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def get(self, path, **kwargs):
        self.calls.append((path, kwargs))
        if path == "users/@me":
            return {"id": "42", "username": "bot"}
        return {"messages": []}


def test_auth_whoami(monkeypatch) -> None:
    client = StubClient()
    monkeypatch.setattr("dread.cli.make_client", lambda: client)
    runner = CliRunner()
    res = runner.invoke(cli, ["auth", "whoami"])
    assert res.exit_code == 0
    assert '"id": "42"' in res.output


def test_mentions_me_user(monkeypatch) -> None:
    client = StubClient()
    monkeypatch.setattr("dread.cli.make_client", lambda: client)
    monkeypatch.setattr("dread.cli.search_mentions", lambda *args, **kwargs: [])
    runner = CliRunner()
    res = runner.invoke(cli, ["mentions", "ls", "--channel", "10", "--user", "me"])
    assert res.exit_code == 0
