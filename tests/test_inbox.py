from __future__ import annotations

from pathlib import Path

from discord_reader.inbox import InboxStore


def test_inbox_store_favorites_and_read_state(tmp_path: Path) -> None:
    store = InboxStore(tmp_path / "inbox.db")
    store.add_favorite("123", label="main")
    store.mark_read("123", "999")

    favs = store.list_favorites()
    assert len(favs) == 1
    assert favs[0].target_id == "123"
    assert store.get_last_read("123") == "999"


def test_inbox_tags(tmp_path: Path) -> None:
    store = InboxStore(tmp_path / "inbox.db")
    store.add_favorite("123")
    store.tag_favorite("123", "alerts")
    rows = store.conn.execute(
        """
        SELECT t.name FROM tags t
        JOIN favorite_tags ft ON t.id = ft.tag_id
        WHERE ft.target_id='123'
        """
    ).fetchall()
    assert [r[0] for r in rows] == ["alerts"]
