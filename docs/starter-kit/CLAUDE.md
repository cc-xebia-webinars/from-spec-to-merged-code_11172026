@AGENTS.md

## Claude Code

- A hook in `.claude/settings.json` formats every file you edit, so you don't need to format files yourself. Another hook refuses edits to test files git already tracks. If it blocks you, fix the code instead, or put new tests in a new file.
- The agent team lives in `.claude/agents/`: a `coordinator` that splits the work and never edits, `implementor`s that build one slice each, and a read-only `verifier`. Start the coordinator with `claude --agent coordinator`.
- `/spec-to-tests <spec>` turns a spec's acceptance criteria into failing tests, and `/verify-against-spec <spec>` checks a change against its spec.
- A hook records what each agent costs in `.claude/cost-ledger.jsonl`. Report it with `<command to run cost_ledger.py --report>`.
