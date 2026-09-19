# Demo 1: Ground Truth: Context and an Executable Spec

In this demo you'll set Roombook up so that every agent that works on it starts from the same facts. You'll read the instruction files and the shared settings, connect a small MCP server that answers questions about the sample data, and turn a written spec into failing acceptance tests. Then you'll have Claude plan the feature against the spec before anyone writes a line of code.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/)
- The [Claude Code CLI](https://code.claude.com/docs/en/setup), signed in with a Claude Pro, Max, Ultra, Team, or Enterprise plan or a Claude Console account

Open this folder as its own VS Code window, and trust it if VS Code asks. Open a terminal in VS Code (**Terminal** > **New Terminal**) and install the dependencies:

```
uv sync
```

Then run the tests:

```
uv run pytest
```

All 62 pass. Roombook is a small FastAPI service for booking meeting rooms in an Amsterdam office and a New York office. It stores times in UTC and shows them in each office's local time, and it already supports weekly recurring bookings.

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/` | The Roombook API |
| `AGENTS.md` | The project instructions every coding agent reads |
| `CLAUDE.md` | Imports `AGENTS.md` and adds notes only Claude Code needs |
| `.claude/settings.json` | Shared permissions and hooks for Claude Code |
| `.mcp.json` | Tells Claude Code how to start the `roombook-facts` MCP server |
| `facts/` | The `roombook-facts` server: read-only facts about the sample data, the clock changes, and the specs |
| `.claude/skills/spec-to-tests/` | A skill that turns a spec's acceptance criteria into failing tests |
| `docs/specs/weekly-allowance.md` | The spec for the feature this session builds |
| `tests/` | 62 tests |

## Presentation Trail

### Part 1: The context every agent shares

#### Step 1: Read the instruction files

Open `AGENTS.md`. Most coding agents look for this file, including Claude Code, GitHub Copilot, Cursor, and OpenAI Codex, so it's the one place to write down what an agent can't work out from the code:

- **Commands** gives the exact commands to install, test, format, and run the app. The note about `pipx install uv` is for an agent working on a machine that doesn't have uv yet, such as a cloud agent in Demo 3 whose setup steps didn't run.
- **How it fits together** explains the conventions that trip people up, such as times stored in UTC and days that aren't always 24 hours long.
- **Specs and ground truth** says where specs live, that acceptance tests are written from the spec before the code, and that the `roombook-facts` server answers questions about the data.
- **Rules** lists what the agent mustn't do, such as edit an existing test to make code pass.

Then open `CLAUDE.md`. Claude Code reads `AGENTS.md` on its own only when a project has no `CLAUDE.md`, so a project with both imports the shared file. The first line, `@AGENTS.md`, does that for every Claude Code session, and the rest is only for Claude.

#### Step 2: Read the shared settings

Open `.claude/settings.json`. It's checked in, so everyone who clones the repository gets the same setup:

- `defaultMode` set to `default` starts every session in Manual mode, where Claude asks before it edits a file or runs a command that could change something.
- `allow` lets Claude run the tests and Ruff, and call the `roombook-facts` tools, without asking. Each command rule appears twice, because Claude Code runs commands through Bash or PowerShell depending on the machine.
- `deny` blocks `git push`, so publishing stays a person's decision, and stops Claude's file tools from reading this README, which is written for you.
- `claudeMdExcludes` stops Claude from loading the instruction files at the top of this webinar repository, which are for the people who maintain it.
- The two hooks run on every edit. One refuses changes to test files that git already tracks, and the other formats each file Claude writes.

### Part 2: Ground truth from an MCP server

#### Step 3: Read the server

Open `facts/server.py`. It's a small MCP server, written with the official MCP Python SDK, with four tools:

- `list_bookings` lists the sample bookings with both local and UTC times, and how long each one is.
- `clock_changes` lists the moments an office's clocks change in a year.
- `db_schema` returns the database's `CREATE` statements.
- `spec_criteria` returns a spec's numbered acceptance criteria, word for word.

Notice that it opens the database with `mode=ro` and marks every tool as read-only. An agent can call it as often as it likes, and nothing it does can change the data. Then open `.mcp.json`, which tells Claude Code to start the server with `uv run python -m facts`.

#### Step 4: Start Claude and approve the server

In the terminal, start Claude Code:

```
claude
```

If Claude asks whether you trust the files in this folder, say yes. Claude then tells you it found a new MCP server in `.mcp.json` and asks whether to use it. Choose to use it. A server listed in a project file runs code on your machine, so each person approves it once, rather than the repository approving it for them.

Check that it's connected:

```text
/mcp
```

`roombook-facts` is listed as connected, with its four tools. Press **Esc** to close the list.

#### Step 5: Ask a question the facts can answer

Send this prompt:

```text
How many hours of bookings does Ava Thompson have in New York in the week of Monday 26 October 2026, and when do New York's clocks change near that week?
```

Claude calls `list_bookings` and `clock_changes` without asking, because of the allow rule. The answer is 4.5 hours: a launch rehearsal on Tuesday evening, which is already Wednesday in UTC, and a partner workshop on Friday. New York's clocks go back early on Sunday 1 November. Claude got those facts from a tool instead of reading the seed data and working out time zones in its head, and so will every other agent that works on Roombook.

### Part 3: An executable spec

#### Step 6: Read the spec

Open `docs/specs/weekly-allowance.md`. Every section is there for the agent as much as for people:

- **Goal** says why the office managers want the feature.
- **Context** points at the code to build on and at the `roombook-facts` server.
- **The Rule** defines the allowance precisely, down to the message a person gets.
- **Constraints** rule out the shortcuts an agent might take, such as a new dependency.
- **Acceptance Criteria** say exactly what done means, using real people and times from the sample data.
- **Out of Scope** lists what not to build, even when it would be easy.

Criterion 3 is the one to watch. A booking from 19:00 to 21:00 on Sunday 1 November in New York starts at midnight on Monday in UTC. In New York time it's still the week of 26 October, where Ava already has 4.5 hours, so it must be rejected.

#### Step 7: Read the skill

Open `.claude/skills/spec-to-tests/SKILL.md`. A skill is a reusable set of instructions that Claude loads when its description matches the task, or when you run it as a command:

- The `description` tells Claude when the skill applies, and `argument-hint` shows what to pass when you run it.
- `$ARGUMENTS` is replaced with whatever you type after the command, here the spec's name.
- The steps get the criteria from the MCP server, check the sample data, write one test per criterion with expected values copied from the spec, and forbid touching production code.

#### Step 8: Turn the spec into tests

Run the skill:

```text
/spec-to-tests weekly-allowance
```

Watch Claude call `spec_criteria` and `list_bookings` before it writes anything. When it asks to create `tests/acceptance/test_weekly_allowance.py`, read the tests and approve the file.

#### Step 9: Run the acceptance tests

In a second terminal (select **+** in the terminal panel), run the new tests:

```
uv run pytest tests/acceptance
```

Four tests fail, for criteria 1, 3, 6, and 7, because nothing enforces an allowance yet. The tests for criteria 2, 4, and 5 already pass. They check that a booking is accepted, so they're there to catch an implementation that goes too far, such as one that counts cancelled bookings or adds up hours across both offices.

Open the test for criterion 3 and check that it books Sunday 1 November from 19:00 to 21:00 and expects `409`. If your tests differ from ours, compare them with [the version Demo 2 starts from](../02-agent-team/tests/acceptance/test_weekly_allowance.py).

### Part 4: Plan before code

#### Step 10: Ask for a plan

Back in the Claude terminal, press **Shift+Tab** until the mode under the prompt shows **⏸ plan mode on**, and send this prompt:

```text
Plan how to implement docs/specs/weekly-allowance.md so the tests in tests/acceptance pass. Split the work into slices that different agents could build, and for each slice name the files it touches and the functions it adds, with their signatures. Say which slices can be built at the same time.
```

In plan mode Claude reads and plans, but it can't change anything.

#### Step 11: Review the plan

Read the plan for three things:

- **The week.** Does it work out the week from local midnights in the office's time zone, and not from a UTC date?
- **The slices.** Does each slice name its files and signatures, so two agents could build different slices at the same time without colliding?
- **The constraints.** Does any slice add a dependency, change `policies.py`, or touch an existing test?

If something's wrong, you'd choose **No, keep planning** and tell Claude what to change. You don't need to approve or save this plan, though. Demo 2's folder starts from a reviewed version of it, in `docs/plans/weekly-allowance.md`, and hands it to a team of agents. When you've finished reading, choose **No, keep planning**, then end the session:

```text
/exit
```

## What You Saw

- `AGENTS.md` gives every agent the same project facts, and `CLAUDE.md` imports it and adds what only Claude needs. Shared settings decide what runs without asking and what never runs.
- An MCP server turns the facts an agent would otherwise guess at into tool calls. A read-only server is safe to call freely, and each person approves a project's server once.
- A spec becomes executable when each acceptance criterion is a test written before the code, with expected values taken from the spec.
- A plan that names files and signatures for each slice is what lets several agents build at the same time.
