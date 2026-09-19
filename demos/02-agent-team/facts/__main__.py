"""Run the facts server over stdio: `uv run python -m facts`."""

from facts.server import server

server.run("stdio")
