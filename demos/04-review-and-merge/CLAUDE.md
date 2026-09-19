@AGENTS.md

## Claude Code

- A hook in `.claude/settings.json` runs `uv run ruff format` after every edit, so you don't need to format files yourself. Another hook blocks edits to test files git already tracks.
- `.claude/settings.json` lets you run `uv run pytest`, `uv run ruff`, and the read-only `git status`, `git diff`, and `git log`, and call the `roombook-facts` tools, without asking. Every other command still needs approval, and `git push` is denied.
- Reusable workflows live in `.claude/skills/`: `/spec-to-tests <spec>` turns a spec's acceptance criteria into failing tests, and `/verify-against-spec <spec>` checks a change against its spec.
- The agent team lives in `.claude/agents/`: a `coordinator` that splits the work and never edits, `implementor`s that build one slice each, and a read-only `verifier`. Start the coordinator with `claude --agent coordinator`.
- A hook records what each agent costs in `.claude/cost-ledger.jsonl`. Report it with `uv run python .claude/hooks/cost_ledger.py --report`.
