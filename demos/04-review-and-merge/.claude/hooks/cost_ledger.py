"""Keep a ledger of what each agent in a session cost, and report it per agent.

Claude Code shows the session's total cost (in /usage and the status line), but not what each
subagent cost. Every transcript records the model and the token usage of each response, though,
so this hook reads them and prices them.

- On SubagentStop, it appends one line per finished subagent to .claude/cost-ledger.jsonl.
- On Stop, it appends a line for the main session so far. The report uses the latest one.

Run `uv run python .claude/hooks/cost_ledger.py --report` to see the totals per agent.

The cost is an estimate at API list prices. On a Claude subscription it shows what the work would
cost at API rates, not what you're billed.
"""

import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "cost-ledger.jsonl"

# Dollars per million tokens: input, output, and cache reads. Writing to the cache costs 1.25x the
# input price for the 5-minute cache and 2x for the 1-hour cache. Check these against the current
# pricing page before you rely on them; a model missing from the table is reported, not guessed.
# Names are matched by prefix, so a newer model whose name starts with an older one's, such as
# claude-fable-5-2 and claude-fable-5, needs a row of its own or it's priced as the older model.
PRICES = {
    "claude-fable-5-2": (8.00, 40.00, 0.20),
    "claude-fable-5-1": (10.00, 50.00, 0.25),
    "claude-fable-5": (10.00, 50.00, 1.00),
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-opus-5": (5.00, 25.00, 0.50),
    "claude-opus-4-8": (5.00, 25.00, 0.50),
    "claude-opus-4-7": (5.00, 25.00, 0.50),
    "claude-opus-4-6": (5.00, 25.00, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10),
    "claude-sonnet-5": (2.00, 10.00, 0.20),
    "claude-sonnet-4-6": (3.00, 15.00, 0.30),
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-haiku-4-5": (1.00, 5.00, 0.10),
}


def price_for(model: str) -> tuple[float, float, float] | None:
    # Transcripts can carry a suffix such as [1m], so match the longest known prefix.
    for name in sorted(PRICES, key=len, reverse=True):
        if model.startswith(name):
            return PRICES[name]
    return None


def usage_from(transcript: Path) -> dict:
    """Total the token usage in one transcript, priced per model."""
    # A response can be written as several lines that share a message id, so keep the last one.
    messages = {}
    for line in transcript.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict):
            continue
        if entry.get("isSidechain") and "subagents" not in transcript.parts:
            continue  # Older versions kept subagent turns in the main transcript.
        if message.get("usage"):
            messages[message.get("id") or len(messages)] = message

    totals = {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "cost_usd": 0.0}
    models, unpriced = set(), set()
    for message in messages.values():
        usage, model = message["usage"], message.get("model", "unknown")
        if model == "<synthetic>":
            continue
        models.add(model)
        creation = usage.get("cache_creation") or {}
        write_1h = creation.get("ephemeral_1h_input_tokens", 0)
        write_5m = usage.get("cache_creation_input_tokens", 0) - write_1h
        counts = {
            "input": usage.get("input_tokens", 0),
            "cache_write": write_5m + write_1h,
            "cache_read": usage.get("cache_read_input_tokens", 0),
            "output": usage.get("output_tokens", 0),
        }
        for key, value in counts.items():
            totals[key] += value
        prices = price_for(model)
        if prices is None:
            unpriced.add(model)
            continue
        inp, out, read = prices
        totals["cost_usd"] += (
            counts["input"] * inp
            + write_5m * inp * 1.25
            + write_1h * inp * 2
            + counts["cache_read"] * read
            + counts["output"] * out
        ) / 1_000_000
    totals["models"] = sorted(models)
    totals["unpriced_models"] = sorted(unpriced)
    return totals


def subagent_transcript(event: dict) -> Path | None:
    if event.get("agent_transcript_path"):
        return Path(event["agent_transcript_path"])
    # Fall back to where Claude Code keeps subagent transcripts, next to the session's own.
    main, agent_id = event.get("transcript_path"), event.get("agent_id")
    if main and agent_id:
        candidate = Path(main).with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"
        return candidate if candidate.exists() else None
    return None


def record(event: dict) -> None:
    name = event.get("hook_event_name")
    if name == "SubagentStop":
        transcript = subagent_transcript(event)
        entry = {"kind": "subagent", "agent": event.get("agent_type") or "subagent"}
        entry["agent_id"] = event.get("agent_id")
    elif name == "Stop":
        transcript = Path(event["transcript_path"]) if event.get("transcript_path") else None
        # agent_type is only present when the session runs as an agent, as with --agent.
        entry = {"kind": "main", "agent": event.get("agent_type") or "main session"}
    else:
        return
    if transcript is None or not transcript.exists():
        return
    entry |= {"session_id": event.get("session_id"), "at": datetime.now(UTC).isoformat()}
    entry |= usage_from(transcript)
    with LEDGER.open("a", encoding="utf-8") as ledger:
        ledger.write(json.dumps(entry) + "\n")


def money(amount: float) -> str:
    return f"${amount:,.2f}"


def report() -> str:
    if not LEDGER.exists():
        return "No ledger yet. It fills in as agents finish their work."
    entries = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line]
    # The main session is recorded after every turn, so only its latest line counts.
    latest_main = {}
    for entry in entries:
        if entry["kind"] == "main":
            latest_main[entry["session_id"]] = entry
    rows = [e for e in entries if e["kind"] == "subagent"] + list(latest_main.values())

    per_agent = defaultdict(lambda: {"runs": 0, "tokens_in": 0, "output": 0, "cost": 0.0})
    models, unpriced = defaultdict(set), set()
    for row in rows:
        agent = per_agent[row["agent"]]
        agent["runs"] += 1
        agent["tokens_in"] += row["input"] + row["cache_write"] + row["cache_read"]
        agent["output"] += row["output"]
        agent["cost"] += row["cost_usd"]
        models[row["agent"]].update(row["models"])
        unpriced.update(row.get("unpriced_models", []))

    width = max([len("Agent"), *map(len, per_agent)]) + 2
    lines = [
        f"{'Agent':<{width}}{'Runs':>4}  {'Tokens in':>11}  {'Tokens out':>10}  {'Cost':>9}  Models"
    ]
    for name, agent in sorted(per_agent.items(), key=lambda item: -item[1]["cost"]):
        model_list = ", ".join(sorted(models[name])) or "-"
        lines.append(
            f"{name:<{width}}{agent['runs']:>4}  {agent['tokens_in']:>11,}  {agent['output']:>10,}"
            f"  {money(agent['cost']):>9}  {model_list}"
        )
    total = sum(agent["cost"] for agent in per_agent.values())
    lines.append(f"{'Total':<{width}}{'':>4}  {'':>11}  {'':>10}  {money(total):>9}")
    lines.append("Estimated at API list prices from the transcripts' token counts.")
    if unpriced:
        lines.append(f"Not priced (add them to PRICES): {', '.join(sorted(unpriced))}")
    return "\n".join(lines)


def main() -> int:
    if "--report" in sys.argv:
        print(report())
        return 0
    try:
        record(json.load(sys.stdin))
    except Exception as exc:  # noqa: BLE001
        # A broken ledger must never stop an agent's work, so report the problem and carry on.
        print(f"cost ledger: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
