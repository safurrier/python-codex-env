from __future__ import annotations

import click

from discord_reader.channels import get_channel, list_guild_channels
from discord_reader.client import DiscordClient
from discord_reader.guilds import get_guild, list_guilds
from discord_reader.messages import (
    add_reaction,
    list_messages,
    reply_message,
    send_message,
    tail_messages,
)
from discord_reader.search import search_mentions
from dread.config import get_token, set_token
from dread.formatting import message_preview, render_json


@click.group()
def cli() -> None:
    """dread: a minimal Discord REST CLI."""


def make_client() -> DiscordClient:
    return DiscordClient(get_token())


@cli.group()
def auth() -> None:
    pass


@auth.command("set-token")
@click.argument("token")
def auth_set_token(token: str) -> None:
    set_token(token)
    click.echo("Token saved")


@auth.command("whoami")
def auth_whoami() -> None:
    me = make_client().get("users/@me")
    click.echo(render_json(me))


@cli.group()
def guild() -> None:
    pass


@guild.command("ls")
@click.option("--json", "as_json", is_flag=True)
def guild_ls(as_json: bool) -> None:
    items = [g.model_dump() for g in list_guilds(make_client())]
    click.echo(
        render_json(items)
        if as_json
        else "\n".join(f"{g['id']}\t{g['name']}" for g in items)
    )


@guild.command("show")
@click.argument("guild_id")
def guild_show(guild_id: str) -> None:
    click.echo(render_json(get_guild(make_client(), guild_id).model_dump()))


@cli.group()
def channel() -> None:
    pass


@channel.command("ls")
@click.argument("guild_id")
@click.option("--type", "type_filter", type=int)
@click.option("--json", "as_json", is_flag=True)
def channel_ls(guild_id: str, type_filter: int | None, as_json: bool) -> None:
    channels = list_guild_channels(make_client(), guild_id)
    if type_filter is not None:
        channels = [c for c in channels if c.type == type_filter]
    items = [c.model_dump() for c in channels]
    click.echo(
        render_json(items)
        if as_json
        else "\n".join(f"{c['id']}\t{c.get('name', '')}" for c in items)
    )


@channel.command("show")
@click.argument("channel_id")
def channel_show(channel_id: str) -> None:
    click.echo(render_json(get_channel(make_client(), channel_id).model_dump()))


@cli.group()
def msg() -> None:
    pass


@msg.command("ls")
@click.argument("channel_id")
@click.option("--limit", default=50, type=int)
@click.option("--before")
@click.option("--after")
@click.option("--json", "as_json", is_flag=True)
def msg_ls(
    channel_id: str, limit: int, before: str | None, after: str | None, as_json: bool
) -> None:
    msgs = list_messages(
        make_client(), channel_id, limit=limit, before=before, after=after
    )
    items = [m.model_dump(mode="json") for m in msgs]
    click.echo(
        render_json(items)
        if as_json
        else "\n".join(f"{m['id']}\t{message_preview(m['content'])}" for m in items)
    )


@msg.command("tail")
@click.argument("channel_id")
@click.option("--pages", default=1, type=int)
@click.option("--limit", default=50, type=int)
def msg_tail(channel_id: str, pages: int, limit: int) -> None:
    msgs = tail_messages(make_client(), channel_id, pages=pages, limit=limit)
    click.echo(render_json([m.model_dump(mode="json") for m in msgs]))


@cli.command("send")
@click.argument("channel_id")
@click.option("--text", required=True)
def send(channel_id: str, text: str) -> None:
    click.echo(
        render_json(
            send_message(make_client(), channel_id, text=text).model_dump(mode="json")
        )
    )


@cli.command("reply")
@click.argument("channel_id")
@click.argument("message_id")
@click.option("--text", required=True)
def reply(channel_id: str, message_id: str, text: str) -> None:
    message = reply_message(make_client(), channel_id, message_id, text=text)
    click.echo(render_json(message.model_dump(mode="json")))


@cli.command("react")
@click.argument("channel_id")
@click.argument("message_id")
@click.argument("emoji")
def react(channel_id: str, message_id: str, emoji: str) -> None:
    add_reaction(make_client(), channel_id, message_id, emoji)
    click.echo("ok")


@cli.group()
def mentions() -> None:
    pass


@mentions.command("ls")
@click.option("--guild", "guild_id")
@click.option("--channel", "channel_id")
@click.option("--user", "user_id", required=True)
@click.option("--since")
@click.option("--last", type=int)
@click.option("--limit", default=50, type=int)
@click.option("--json", "as_json", is_flag=True)
def mentions_ls(
    guild_id: str | None,
    channel_id: str | None,
    user_id: str,
    since: str | None,
    last: int | None,
    limit: int,
    as_json: bool,
) -> None:
    if user_id == "me":
        user_id = make_client().get("users/@me")["id"]
    hits = search_mentions(
        make_client(),
        user_id=user_id,
        guild_id=guild_id,
        channel_id=channel_id,
        since=since,
        last=last,
        limit=limit,
    )
    if as_json:
        click.echo(
            render_json(
                [h.model_dump(mode="json") | {"jump_url": h.jump_url} for h in hits]
            )
        )
        return
    for hit in hits:
        ts = hit.message.timestamp.astimezone().isoformat(timespec="seconds")
        click.echo(
            f"{hit.channel_id}\t{ts}\t{hit.message.author.username}\t{hit.message.id}\t"
            f"{message_preview(hit.message.content)}\t{hit.jump_url}"
        )


if __name__ == "__main__":
    cli()
