# Discord Route Validation Notes (Bot Token Only)

This project intentionally supports **Discord bot tokens only** (`Authorization: Bot <token>`).
User-token/self-bot flows are out of scope and intentionally unsupported.

## Validation method

Each implemented route is validated in two ways:
1. Code-level route wrapper uses the expected HTTP method/path and query/body fields.
2. Unit tests assert the exact path/params/body construction for wrappers and command flows.

## Route-by-route notes

| Area | Method | Route | Parameters/body validated | Notes |
|---|---|---|---|---|
| Auth identity | GET | `/users/@me` | none | Used by `auth whoami`, and for `mentions --user me`. |
| Guild listing | GET | `/users/@me/guilds` | none | Returns guild summary list for bot user. |
| Guild details | GET | `/guilds/{guild_id}` | path `guild_id` | Used by `guild show`. |
| Guild channels | GET | `/guilds/{guild_id}/channels` | path `guild_id` | Used by `channel ls` and mentions fallback scope expansion. |
| Channel details | GET | `/channels/{channel_id}` | path `channel_id` | Used by `channel show` and thread-safe read behavior. |
| Messages list | GET | `/channels/{channel_id}/messages` | query: `limit`, optional `before`, `after` | Limit clamped to API range [1,100]. |
| Message create | POST | `/channels/{channel_id}/messages` | JSON: `content` | Used by `send`. |
| Message reply | POST | `/channels/{channel_id}/messages` | JSON: `content`, `message_reference.message_id`, `message_reference.channel_id` | Used by `reply`. |
| Add reaction | PUT | `/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me` | path ids + `emoji` | Used by `react`. |
| Search mentions (channel) | GET | `/channels/{channel_id}/messages/search` | query: `mentions`, `limit` | Preferred mentions path where available. |
| Search mentions (guild) | GET | `/guilds/{guild_id}/messages/search` | query: `mentions`, `limit` | Preferred guild-wide mentions path where available. |

## Search fallback behavior

If search endpoints are not available/usable for the environment (`403/404/405/501`), mentions fall back to channel message scanning with:
- exact mention object matching (`mentions[].id == user_id`) preferred,
- then content token matching (`<@id>` / `<@!id>`).

## Retry/rate-limit behavior

`DiscordClient` handles:
- `429` with `Retry-After` delay,
- `202` for index-not-ready paths via `retry_after` payload field,
- bounded retries for transient 5xx with jittered exponential backoff.
