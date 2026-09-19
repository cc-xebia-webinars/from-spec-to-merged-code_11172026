"""The status line: which agent and model are running, how full the context is, and the cost so far.

Claude Code runs this after each update and passes the session's details as JSON on stdin. It has
to be quick, so it only formats what it's given.
"""

import json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    parts = []
    agent = (data.get("agent") or {}).get("name")
    if agent:
        parts.append(f"@{agent}")
    parts.append((data.get("model") or {}).get("display_name", "Claude"))
    used = (data.get("context_window") or {}).get("used_percentage")
    if used is not None:
        parts.append(f"context {used:.0f}%")
    cost = (data.get("cost") or {}).get("total_cost_usd")
    if cost is not None:
        parts.append(f"session ${cost:.2f}")
    print(" | ".join(parts))


if __name__ == "__main__":
    main()
