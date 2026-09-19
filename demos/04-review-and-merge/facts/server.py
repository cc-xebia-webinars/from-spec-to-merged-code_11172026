"""Roombook facts: a read-only MCP server that gives every agent the same ground truth.

Agents are good at guessing and bad at knowing when they've guessed. This server answers the
questions they'd otherwise guess at, such as what's in the sample data, when the clocks change in
each office, what the database looks like, and what a spec's acceptance criteria say. It reads
the same files the app uses and never writes to them, so an agent can call it as often as it
likes without asking.

Claude Code starts it from `.mcp.json` with `uv run python -m facts`.
"""

import re
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from roombook import db, seed, settings
from roombook.offices import OFFICES
from roombook.timeutils import from_db, to_local_text

PROJECT = Path(__file__).resolve().parent.parent
SPECS = PROJECT / "docs" / "specs"

# Every tool only reads, so clients can call them without asking for approval each time.
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True)

server = MCPServer(
    name="roombook-facts",
    instructions=(
        "Read-only facts about Roombook: the sample bookings, each office's clock changes, the "
        "database schema, and the acceptance criteria in docs/specs. Use these tools instead of "
        "working facts out by hand. Times come back in both office time and UTC."
    ),
)


def _connect() -> sqlite3.Connection:
    """Open the sample database read-only, building it first if this checkout has none yet."""
    path = settings.DB_PATH
    if not path.exists():
        # The same first-run setup the app does, so the facts match what the API would serve.
        conn = db.connect(path)
        try:
            db.init_schema(conn)
            if db.is_empty(conn):
                seed.load(conn)
        finally:
            conn.close()
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _office(code: str) -> str:
    code = code.upper()
    if code not in OFFICES:
        # ToolError is the one exception whose message reaches the agent; any other exception
        # arrives only as "Error executing tool", which leaves it guessing at the right code.
        raise ToolError(f"Unknown office {code!r}. Offices: {', '.join(OFFICES)}.")
    return code


@server.tool(annotations=READ_ONLY)
def list_bookings(
    booked_by: str | None = None,
    office: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    include_cancelled: bool = False,
) -> dict:
    """List bookings in the sample data, with both local and UTC times and each one's length.

    Filter by the exact booked_by name, by office code (AMS or NYC), and by an inclusive range of
    local dates (YYYY-MM-DD) in each booking's own office. Cancelled bookings are left out unless
    include_cancelled is true. hours_by_status totals the hours of the bookings returned.
    """
    first = date.fromisoformat(from_date) if from_date else date.min
    last = date.fromisoformat(to_date) if to_date else date.max
    wanted_office = _office(office) if office else None

    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT b.*, r.name AS room_name, r.office FROM bookings b"
            " JOIN rooms r ON r.id = b.room_id ORDER BY b.start_utc, b.id"
        ).fetchall()
    finally:
        conn.close()

    bookings, hours_by_status = [], {}
    for row in rows:
        tz = OFFICES[row["office"]].tz
        start, end = from_db(row["start_utc"]), from_db(row["end_utc"])
        local_day = start.astimezone(tz).date()
        if booked_by is not None and row["booked_by"] != booked_by:
            continue
        if wanted_office is not None and row["office"] != wanted_office:
            continue
        if not first <= local_day <= last:
            continue
        if row["status"] == "cancelled" and not include_cancelled:
            continue
        hours = (end - start) / timedelta(hours=1)
        hours_by_status[row["status"]] = hours_by_status.get(row["status"], 0) + hours
        bookings.append(
            {
                "id": row["id"],
                "office": row["office"],
                "room_id": row["room_id"],
                "room": row["room_name"],
                "title": row["title"],
                "booked_by": row["booked_by"],
                "status": row["status"],
                "local_start": to_local_text(start, tz),
                "local_end": to_local_text(end, tz),
                "local_weekday": start.astimezone(tz).strftime("%A"),
                "utc_start": row["start_utc"],
                "utc_end": row["end_utc"],
                "hours": hours,
                "series_id": row["series_id"],
            }
        )
    return {"bookings": bookings, "hours_by_status": hours_by_status}


@server.tool(annotations=READ_ONLY)
def clock_changes(office: str, year: int = 2026) -> list[dict]:
    """List the moments an office's clocks change in a year, with the local time on each side.

    Pass the office code, AMS or NYC. Useful whenever a calculation crosses a weekend in late October or early November, when the
    gap between Amsterdam and New York shrinks to five hours for a week.
    """
    tz = OFFICES[_office(office)].tz
    changes = []
    moment = datetime(year, 1, 1, tzinfo=UTC)
    offset = moment.astimezone(tz).utcoffset()
    # Clock changes in both offices happen on the hour, so checking each UTC hour finds them all.
    while moment.year == year:
        moment += timedelta(hours=1)
        new_offset = moment.astimezone(tz).utcoffset()
        if new_offset != offset:
            before = moment - timedelta(microseconds=1)
            changes.append(
                {
                    "utc": moment.strftime("%Y-%m-%dT%H:%MZ"),
                    "local_date": moment.astimezone(tz).date().isoformat(),
                    "local_weekday": moment.astimezone(tz).strftime("%A"),
                    "clocks": "go back one hour" if new_offset < offset else "go forward one hour",
                    "utc_offset_before": before.astimezone(tz).strftime("%:z"),
                    "utc_offset_after": moment.astimezone(tz).strftime("%:z"),
                    "local_day_length_hours": _day_hours(moment.astimezone(tz).date(), tz),
                }
            )
            offset = new_offset
    return changes


def _day_hours(day: date, tz) -> float:
    start = datetime.combine(day, datetime.min.time(), tzinfo=tz)
    end = datetime.combine(day + timedelta(days=1), datetime.min.time(), tzinfo=tz)
    return (end.astimezone(UTC) - start.astimezone(UTC)) / timedelta(hours=1)


@server.tool(annotations=READ_ONLY)
def db_schema() -> str:
    """Return the CREATE statements for every table in the sample database."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND sql IS NOT NULL ORDER BY name"
        ).fetchall()
    finally:
        conn.close()
    return "\n\n".join(row["sql"] + ";" for row in rows)


@server.tool(annotations=READ_ONLY)
def spec_criteria(spec: str) -> dict:
    """Return the numbered acceptance criteria from docs/specs/<spec>.md, word for word.

    Pass the file name without the extension, such as "recurring-bookings". Every agent working
    on a spec reads the criteria from here, so they all check against the same list.
    """
    path = SPECS / f"{spec.removesuffix('.md')}.md"
    if not path.is_file():
        available = ", ".join(sorted(p.stem for p in SPECS.glob("*.md"))) or "none"
        raise ToolError(f"No spec named {spec!r}. Specs in docs/specs: {available}.")
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    section = re.search(
        r"^## Acceptance Criteria\s*$(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
    )
    if section is None:
        return {"spec": path.stem, "title": title, "criteria": []}
    # Criteria are a numbered list, and a criterion can wrap onto indented lines.
    criteria = []
    for line in section.group(1).splitlines():
        match = re.match(r"^(\d+)\.\s+(.*)$", line)
        if match:
            criteria.append({"number": int(match.group(1)), "text": match.group(2).strip()})
        elif line.startswith((" ", "\t")) and line.strip() and criteria:
            criteria[-1]["text"] += " " + line.strip()
    return {"spec": path.stem, "title": title, "criteria": criteria}
