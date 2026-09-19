@AGENTS.md

## Claude Code

- A hook in `.claude/settings.json` runs `uv run ruff format` after every edit, so you don't need to format files yourself. Another hook blocks edits to test files git already tracks.
- `.claude/settings.json` lets you run `uv run pytest` and `uv run ruff`, and call the `roombook-facts` tools, without asking. Every other command still needs approval.
- Reusable workflows live in `.claude/skills/`. Use `/spec-to-tests <spec name>` to turn a spec's acceptance criteria into failing tests.
