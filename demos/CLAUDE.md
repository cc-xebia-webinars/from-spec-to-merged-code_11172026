# Demo Instructions for This Webinar

**If your working folder is a numbered demo folder, such as `demos/01-ground-truth`, ignore this file.** It's written for the people and agents who maintain this webinar repository, not for anyone working through a demo. Follow only the instructions inside your demo folder.

The general rules for demos, including folder naming, `uv` setup, the README structure, and the writing style, are in the `CLAUDE.md` file at the root of the repo. This file adds what's specific to this webinar.

## Tools

- **The Claude Code CLI**, run in VS Code's integrated terminal, for all the local work. The walkthroughs use `claude` and `claude --agent <name>`, the permission modes cycled with **Shift+Tab** (Manual, accepting edits automatically, and plan mode; auto mode is in the cycle on some accounts, and the demos don't use it), `/mcp`, `/usage`, `/goal`, `/exit`, project skills run as slash commands, and the status line. Don't write steps for the VS Code extension or for Copilot's **Claude** session target.
- **GitHub Copilot on github.com**, in Demos 3 and 4 only: the **Copilot cloud agent**, started by assigning an issue to `@copilot`, and **Copilot code review**, requested with `gh pr edit --add-reviewer "@copilot"`, with **Fix with Copilot** turning a review comment into a fix pull request. Copilot isn't used inside VS Code.
- **The GitHub CLI** for everything on GitHub that a command can do: creating the repository, the issue, and the pull requests, assigning Copilot, requesting reviews, checking CI, marking pull requests as ready, and merging.
- When a step's wording depends on a tool's interface, check it against the current documentation for that tool before changing it. Copilot's cloud features and labels change often. GitHub renamed the coding agent to the cloud agent in 2026, and on 28 October 2026 it grouped its cloud features under one policy, **Copilot in the cloud**.
- Python 3.14 for everything. Each demo pins it in `pyproject.toml` (`requires-python = "==3.14.*"`) and `.python-version`, and sets `package = false` so Roombook runs in place.
- Every dependency is pinned to an exact version: `fastapi`, `uvicorn`, and `tzdata` (Windows has no time zone database of its own), with `httpx2`, `pytest`, `pytest-cov`, `ruff`, and `mcp` in the `dev` group. Starlette's test client warns about plain `httpx`, which is why the demos use `httpx2`. The `mcp` package is version 2, where the server class is `MCPServer`, not v1's `FastMCP`.
- All Python is formatted with `ruff format` at a line length of 100. The sample data tables in `roombook/seed.py` sit between `# fmt: off` and `# fmt: on`, one row per line.
- The GitHub workflows pin `actions/checkout@v7` and `astral-sh/setup-uv@v10.3.3`. setup-uv no longer publishes a moving major tag, so pin its exact release. A cloud agent session runs either in a cloud sandbox, the default since 28 October 2026, or on GitHub Actions, and `copilot-setup-steps.yml` runs only on Actions. The docs don't say which one an issue assignment uses, so check the session log in each rehearsal. The workflow must stay on the default branch, with a single job named `copilot-setup-steps`. `AGENTS.md` tells the agent to use `pipx install uv` if uv is missing, which covers the sandbox, and because plain `pip install` can fail on Ubuntu runners, whose Python is externally managed.
- Accept-edits mode runs simple file commands, such as `rm`, `mv`, and `sed`, inside the project without asking, and the `protect_tests.py` hook only watches the edit tools. Don't write that every unlisted command asks, and keep the `/goal` condition's check that tracked tests haven't changed.
- Requesting a review from `@copilot` with `gh pr edit` needs gh 2.88 or later.

## Outside Services

Claude Code, GitHub, and GitHub Copilot are the only services a demo may use beyond the presenter's machine. Demos 1 and 2 run offline, apart from Claude Code, once `uv sync` has run. Demos 3 and 4 publish a private repository to the attendee's own GitHub account and use Copilot there.

## The Codebase

Every demo works on Roombook, a FastAPI and SQLite API for booking meeting rooms in Amsterdam (`Europe/Amsterdam`) and New York (`America/New_York`). Times are stored in UTC and sent and shown in office time. The sample data is fixed, with no randomness, so every machine gets the same results, and `roombook/settings.py` pins the app's clock to Monday 26 October 2026, so the sample bookings never fall into the past. The starting code is the finished Roombook from the previous webinar, with weekly recurring bookings, and 62 tests.

The feature is the weekly allowance in `docs/specs/weekly-allowance.md`: at most 6 hours of confirmed or pending bookings per person, per office, per local week. Each demo folder holds its own copy of Roombook at the state the previous demo leaves it in:

| Demo | Folder | Starts with |
|------|--------|-------------|
| 1 | `01-ground-truth` | Roombook (62 tests), `AGENTS.md`, `CLAUDE.md`, the `roombook-facts` MCP server in `facts/` and `.mcp.json`, the `spec-to-tests` skill, and the spec |
| 2 | `02-agent-team` | Demo 1's end: the acceptance tests (4 fail, 3 pass) and the plan in `docs/plans/`, plus the three agents, the `verify-against-spec` skill, the cost ledger hook, and the status line (65 pass, 4 fail) |
| 3 | `03-loops-and-verification` | Demo 2's starting code, plus `.github/` and the issue in `issues/`. Attendees copy the agent team's first pass in from `demos/reference/team-build/` (after the copy: 74 pass, 2 fail) |
| 4 | `04-review-and-merge` | The feature branch as it should be at the end of Demo 3 (75 tests). The demo itself carries on in the attendee's Demo 3 repository |

`demos/reference/04-review-and-merge` is the finished run, with the cloud agent's schedule change merged too (76 tests).

## Deliberate Problems

`demos/reference/team-build/` is a deterministic stand-in for the agent team's output, which Demo 3 copies over its code, so the verification step finds the same things every time. It lives outside the Demo 3 folder because attendees publish that folder as a repository of their own. Don't move it inside and ignore it there: git applies a demo folder's `.gitignore` to this repository too, so the overlay would silently drop out of the webinar repository. It wires the allowance into new bookings only, so criteria 6 and 7 fail and the `/goal` loop has work to do. It also carries three problems that every test passes, which the verifier is meant to find. Demo 3's README names them in Step 10, and the presenter's teaching guide explains how to handle them live.

- Never describe these problems in a file the agents read in Demo 3, such as code comments, `AGENTS.md`, `CLAUDE.md`, the agent files, the skills, test names, the issue, or `pyproject.toml`. The walkthrough `README.md` is the exception, because it has to tell people what to look for, and the settings deny Claude access to it.
- Keep the problems invisible to the tests. In particular, no acceptance criterion may mention pending bookings, and the verifier's fix adds the pending-bookings test in a new file, `tests/test_allowance.py`, because the hook blocks edits to tracked test files. In Demo 3's fix, the person runs `git rm tests/test_people.py`, Claude fixes the code in accept-edits mode, and then the person runs `uv remove python-dateutil`. Keep that order: the facts server imports `roombook.timeutils`, so it can't start while `week_bounds` still needs the removed package.
- When you change Roombook or the feature, rebuild `team-build/` from Demo 3's starting code, so that it applies cleanly, its `pyproject.toml` keeps Demo 3's name, and `uv.lock` matches it. Then check that the copy leaves exactly 74 passing and 2 failing tests.
- A demo folder's `.gitignore` also applies to this repository, so it must never ignore anything the webinar repository needs to ship.

## Keeping the Agents to the Demo

Agents read more than the code, so every demo is set up to give them the demo's context and nothing else:

- Each demo's `.claude/settings.json` has a `claudeMdExcludes` setting with the patterns `**/!(0[1-4]-*)/CLAUDE.md` and `**/!(0[1-4]-*)/AGENTS.md`. Claude Code loads these files from every parent folder, so without it, this file and the root `CLAUDE.md` and `AGENTS.md` would load into every demo session. That's why the reference copy is also in a numbered folder, and why a new demo folder must keep the two-digit prefix. A fifth demo needs `0[1-5]` in every pattern.
- The same settings deny `Read(./README.md)`, so Claude can't read the walkthrough.
- From Demo 2 on, attendees run `git init` inside the demo folder. The demo becomes its own repository, so the agents' diffs show only their work, and the repository Demo 3 publishes holds only the demo's files. Each demo folder therefore has its own `.gitignore`.
- Nothing that answers a demo's exercise goes inside that demo's folder. The finished code and the team build live in `demos/reference/`.
- `pyproject.toml` descriptions and file names in a demo folder mustn't hint at a problem the demo asks an agent to find.

## Carrying Changes Forward

A change to Roombook, its sample data, the spec, the agents, the skills, or the hooks has to be carried forward through every later demo and the reference folder. Then check the numbers the READMEs quote: the test counts (62, 65 and 4, 74 and 2, 76, 75, and 76), the 27 bookings, Ava Thompson's 4.5 hours in the week of 26 October, and the acceptance criteria's dates and times.

## Coverage

Between them, the demos cover the agenda in the repo `README.md`:

- **What changed in 2026.** The slides cover it. The demos show a coordinator agent starting subagents in parallel (Demo 2), a cloud agent (Demo 3), agentic review (Demo 4), and token costs (Demos 2 and 4).
- **Spec-driven development.** Demo 1: a spec with numbered criteria, turned into failing tests before any code, and a plan written in plan mode against it.
- **Agent teams.** Demo 2: a coordinator, implementors, and a verifier, with scoped tools, permission modes, and models, slices run in parallel, and a per-agent cost ledger.
- **Context engineering.** Demo 1: `AGENTS.md`, `CLAUDE.md`, shared settings, a skill, and the read-only `roombook-facts` MCP server that every agent queries. Demo 4's review instructions do the same for Copilot.
- **Autonomous loops.** Demo 3: `/goal` drives a local test-fix loop with a bounded condition while Copilot's cloud agent works an issue into a draft pull request. `/loop` and `Stop` hooks are mentioned.
- **Adversarial verification.** Demo 3: a fresh verifier finds scope creep, drift from the spec, and a broken constraint that every test passes.
- **Closing the loop.** Demo 4: Copilot code review, a fix pull request from **Fix with Copilot**, CI, and a merge checklist a person works through.
- **Cost and governance.** Demos 2 and 4 add up the cost. Demo 4 shows where GitHub keeps people in the loop, and the slides cover where to draw the autonomy line.
