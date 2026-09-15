# Connect FactIQ

FactIQ uses the bundled `factiq` remote MCP server and FactIQ OAuth. Do not ask
the user for an API key, access token, or password. The user completes sign-in
in FactIQ's browser flow.

The one exception is a headless environment (CI, a server, a scripted agent
run) where no browser can open. There the user creates a personal API key at
[factiq.com/settings/security](https://www.factiq.com/settings/security) and
registers the server with it themselves; see
[Headless environments](#headless-environments) below. Never ask the user to
paste the key into the chat.

## Claude Code

1. If the plugin was installed in the current session, ask the user to run
   `/reload-plugins` so Claude Code loads the bundled MCP configuration.
2. Ask the user to run `/mcp` and select `factiq`.
3. Ask the user to choose **Authenticate** or **Connect**. Claude Code opens the
   FactIQ sign-in page in a browser.
4. Wait for the user to finish signing in with email, Google, or a passkey and
   return to Claude Code.
5. Run `/mcp` again and confirm that `factiq` is connected. If the server was
   already connected before a plugin update, reconnect it so Claude refreshes
   the current tool list.

Claude Code may use a loopback callback with a changing local port. This is
expected; the user does not need to configure or copy a callback URL.

## Claude web, desktop, and Cowork

Cowork has no terminal, so use only the Claude interface:

1. Open **Customize → Plugins** and select the installed **FactIQ** plugin.
2. Choose **Connect** for the bundled FactIQ connector.
3. Complete the FactIQ browser sign-in with email, Google, or a passkey, then
   return to Claude.
4. Confirm that FactIQ shows as connected. If Claude reports stale or missing
   tools after an update, disconnect and reconnect FactIQ to refresh its tool
   list.

## Headless environments

When no browser is available, the user registers the MCP server with an API
key instead of signing in. Point them to
[factiq.com/docs/api](https://www.factiq.com/docs/api) for the full guide. The
short form:

```bash
# Claude Code
claude mcp add factiq https://api.factiq.com/mcp --transport http \
  --header "Authorization: Bearer $FACTIQ_API_KEY"

# Codex
codex mcp add factiq --url https://api.factiq.com/mcp \
  --bearer-token-env-var FACTIQ_API_KEY
```

The key must come from the user's own environment. Do not read it from a file,
print it, or write it into a commit.

## Verify the connection

Ask: **Use FactIQ to list the available data schemas.** A working connection
calls `get_data_catalog` and returns the live FactIQ catalog. Do not use another
data source for this check.

If authentication is stuck, sign in to [FactIQ](https://www.factiq.com) in the
same browser and retry **Connect**. Setup instructions and current plan support
are maintained at [factiq.com/claude](https://www.factiq.com/claude) and
[factiq.com/claude-code](https://www.factiq.com/claude-code).
