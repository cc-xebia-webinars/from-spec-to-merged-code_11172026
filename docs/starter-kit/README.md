# Agent Team Starter Kit

These files are a starting point for running coding agents as a coordinated team on your own repository, based on what the webinar's demos built. Copy them in, replace the parts in angle brackets, and review them with your team like any other code. Keep every file short: agents load the instructions into every session, and so do the people who maintain them.

## Context and Specs

| File | Copy it to | What it does |
|------|-----------|--------------|
| [AGENTS.md](./AGENTS.md) | `AGENTS.md` at the root of your repository | The project instructions that Claude Code, Copilot, Cursor, OpenAI Codex, and most other agents read |
| [CLAUDE.md](./CLAUDE.md) | `CLAUDE.md` next to `AGENTS.md` | Imports `AGENTS.md` for Claude Code, which reads a `CLAUDE.md` instead of `AGENTS.md` when both exist, plus anything only Claude needs |
| [mcp.json](./mcp.json) | `.mcp.json` | Starts a project MCP server, such as a read-only facts server, for Claude Code |
| [spec-template.md](./spec-template.md) | `docs/specs/<feature>.md` | A spec with numbered acceptance criteria, written for agents as much as for people |

## The Agent Team

| File | Copy it to | What it does |
|------|-----------|--------------|
| [agents/coordinator.md](./agents/coordinator.md) | `.claude/agents/coordinator.md` | Splits a plan into slices and delegates them. It has no edit tools |
| [agents/implementor.md](./agents/implementor.md) | `.claude/agents/implementor.md` | Builds one slice, on a cheaper model, with edits accepted automatically |
| [agents/verifier.md](./agents/verifier.md) | `.claude/agents/verifier.md` | Checks a change against its spec. It's read-only |
| [skills/spec-to-tests/SKILL.md](./skills/spec-to-tests/SKILL.md) | `.claude/skills/spec-to-tests/SKILL.md` | Turns a spec's criteria into failing acceptance tests |
| [skills/verify-against-spec/SKILL.md](./skills/verify-against-spec/SKILL.md) | `.claude/skills/verify-against-spec/SKILL.md` | The verifier's checklist |

## Guardrails and Costs

| File | Copy it to | What it does |
|------|-----------|--------------|
| [claude-settings.json](./claude-settings.json) | `.claude/settings.json` | Shared permissions, the status line, and four hooks |
| [hooks/protect_tests.py](./hooks/protect_tests.py) | `.claude/hooks/protect_tests.py` | Refuses edits to test files git already tracks |
| [hooks/format_edited.py](./hooks/format_edited.py) | `.claude/hooks/format_edited.py` | Formats only the file the agent just edited |
| [hooks/cost_ledger.py](./hooks/cost_ledger.py) | `.claude/hooks/cost_ledger.py` | Records what each agent costs, and reports it with `--report` |
| [statusline.py](./statusline.py) | `.claude/statusline.py` | Shows the agent, model, context, and session cost under the prompt |

## GitHub and Copilot

| File | Copy it to | What it does |
|------|-----------|--------------|
| [github/ci.yml](./github/ci.yml) | `.github/workflows/ci.yml` | Runs the tests on every pull request, including the agents' |
| [github/copilot-setup-steps.yml](./github/copilot-setup-steps.yml) | `.github/workflows/copilot-setup-steps.yml` | Installs uv and the dependencies before Copilot's cloud agent starts work in the Actions environment |
| [github/review.instructions.md](./github/review.instructions.md) | `.github/instructions/review.instructions.md` | Tells Copilot code review to review against the spec |

## Adapting It

- The files assume a Python project run with `uv`, tests in `tests/`, and Ruff for formatting. Change the commands in the settings, the CI workflow, and `format_edited.py` to the ones your project uses.
- Replace `<facts-server>` with the name of your MCP server in `.mcp.json`, the settings, and the agents' `tools`. If you don't have one, remove the `mcp__` entries.
- Each allow and deny rule appears twice, once for Bash and once for PowerShell, because Claude Code runs commands through one or the other depending on the machine.
- Pick each agent's model for its job. The implementors do most of the reading and writing, so a cheaper model there has the biggest effect on the bill.
- `cost_ledger.py` prices tokens from a table at the top of the file. Check it against Anthropic's current prices, and add any model your team uses.
- Hooks are configured per tool. These are Claude Code hooks, so check how each other agent your team uses enforces the same rules, and keep CI as the final safeguard.

## Before You Rely on It

- Ask an agent to break each rule on purpose, such as editing an existing test or running `git push`, and confirm it's stopped. Try deleting a test from the shell in accept-edits mode too. That mode runs simple file commands such as `rm` without asking, and `protect_tests.py` only watches the edit tools, so CI is what catches it.
- Run the verifier on a change you know has a problem, and check that it finds it.
- Assign a small issue to Copilot's cloud agent, and read its session log to check it found your instructions and could install your tools.
- Revisit `AGENTS.md`, the spec template, and the verifier's checklist whenever an agent session teaches you something. Add the lesson in one line.

The [Spec-to-Merge Checklist](../spec-to-merge-checklist.md) covers the rest of the workflow, from writing the spec to the merge decision.
