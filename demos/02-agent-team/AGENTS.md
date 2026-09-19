# Roombook

A FastAPI and SQLite API for booking meeting rooms in the Amsterdam and New York offices. `README.md` in this folder is a walkthrough for the people running a demo, not documentation of Roombook, so don't use it as a source.

## Commands

- Install dependencies: `uv sync`. If `uv` isn't installed, install it with `pipx install uv` first.
- Run the tests: `uv run pytest`
- Check coverage: `uv run pytest --cov --cov-report=term-missing`
- Format and lint: `uv run ruff format` and `uv run ruff check`
- Run the API: `uv run uvicorn roombook.main:app --reload`, then open http://127.0.0.1:8000/docs
- Rebuild the sample database: `uv run python -m roombook.seed --reset`

## How it fits together

- `roombook/main.py` builds the app with `create_app()`. Routes live in `roombook/routes/`, one module per resource.
- Times are stored in UTC, as text in the format `timeutils.DB_FORMAT`. Requests and responses use the office's local time, without an offset. Use the helpers in `roombook/timeutils.py` for every conversion.
- A day in an office runs from local midnight to local midnight, and it isn't always 24 hours long. Use `timeutils.day_bounds` rather than adding 24 hours to a UTC time.
- Every new or moved booking goes through `check_slot` in `roombook/slots.py`, which applies the rules in `roombook/policies.py` and checks for clashes. The rules come from the office managers, so don't change one unless you're asked to.
- Weekly recurring bookings live in `roombook/series.py`. Each occurrence is an ordinary booking with a `series_id`.
- Routes get the database connection and the current time from `roombook/deps.py`. Tests override `get_now`, and `roombook/settings.py` pins the app's clock to the sample data's fortnight.
- Tests use the `client` fixture in `tests/conftest.py`, which gives each test its own freshly seeded database.

## Specs and ground truth

- Features start as a spec in `docs/specs/`. Each spec ends with numbered acceptance criteria, and those criteria are the definition of done. The plan for building a spec, split into slices, goes in `docs/plans/`.
- Acceptance tests live in `tests/acceptance/`, one test per criterion, and they're written from the spec before the code.
- The `roombook-facts` MCP server (`facts/`, set up in `.mcp.json`) answers questions about the sample data, each office's clock changes, the database schema, and a spec's acceptance criteria. Ask it rather than working facts out by hand. It only reads.

## Rules

- Don't edit an existing test to make code pass. If a test looks wrong, stop and explain why.
- Ask before adding a dependency, and add it with `uv add`, never `pip install`.
- For existing behavior, expected values in tests come from running the code. For new behavior, they come from the spec. Never work them out by hand.
- Keep each change small, and run `uv run pytest` after it.
