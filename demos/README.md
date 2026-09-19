# Demos

These four demos take one feature from a written spec to merged code, on one codebase: Roombook, a small FastAPI service for booking meeting rooms in an Amsterdam office and a New York office. The feature is a weekly booking allowance. Claude Code does the local work, run as a team of agents in VS Code's terminal, and on GitHub, Copilot's cloud agent and Copilot code review do the cloud work. Each demo starts where the previous one leaves off, and each has its own copy of the code and its own `uv` project pinned to Python 3.14.

| # | Demo | Description | Time |
|---|------|-------------|------|
| 1 | [Ground Truth: Context and an Executable Spec](./01-ground-truth/README.md) | Shared instruction files and settings, a read-only MCP server that gives every agent the same facts, a skill that turns the spec's acceptance criteria into failing tests, and a plan written before any code. | 15 min |
| 2 | [An Agent Team Builds the Feature](./02-agent-team/README.md) | A coordinator that can't edit, implementors that build slices in parallel, and a read-only verifier, each with scoped tools and its own model, and a ledger of what each agent cost. | 18 min |
| 3 | [Loops, a Cloud Agent, and a Second Opinion](./03-loops-and-verification/README.md) | Copilot's cloud agent works an issue into a draft pull request while `/goal` drives a local test-fix loop, and then a verifier finds scope creep and drift that every test passes. | 18 min |
| 4 | [Review, Fix, Merge, and the Bill](./04-review-and-merge/README.md) | Review and merge the cloud agent's pull request, get an agentic code review, hand a finding back as a fix pull request, add up the cost, and make the merge decision. | 17 min |

## Getting Ready

Every demo needs these tools:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later. It installs Python 3.14 for you if you don't have it.
- [Visual Studio Code](https://code.visualstudio.com/).
- The [Claude Code CLI](https://code.claude.com/docs/en/setup), signed in with a Claude Pro, Max, Ultra, Team, or Enterprise plan or a Claude Console account.

Demos 3 and 4 also need:

- The [GitHub CLI](https://cli.github.com/) 2.88 or later, signed in with `gh auth login`.
- A GitHub account with a [Copilot plan that includes the cloud agent and code review](https://docs.github.com/en/copilot/get-started/plans): Copilot Student, Pro, Pro+, Max, Business, or Enterprise. On Business and Enterprise, check with your administrator that the **Copilot in the cloud** policy and code review are on; the cloud policy is on by default. Copilot Free doesn't include them.

Run `uv sync` in each demo folder while you're online. After that, everything in Demos 1 and 2 runs offline except Claude Code itself. Demos 3 and 4 also use GitHub.

Open each demo as its own VS Code window, for example `code demos/02-agent-team`. On macOS, install the `code` command first: open the Command Palette and run **Shell Command: Install 'code' command in PATH**. Opening the demo folder directly keeps Claude working on that demo's code. If VS Code asks whether you trust the authors of the files in the folder, select **Yes, I trust the authors**, and do the same when Claude Code asks. Claude Code ignores a folder's allow rules, and won't start its MCP servers, until you trust it.

### Claude Code in the Terminal

The demos run the Claude Code CLI in VS Code's integrated terminal (**Terminal** > **New Terminal**), with the editor beside it for reading files and diffs. Start it with `claude`, or with `claude --agent <name>` to make one of the project's agents the main one. Press **Shift+Tab** to move between the permission modes: Manual, where Claude asks before it edits a file or runs a command that could change something, accepting edits automatically, and plan mode. If your account has auto mode, it's in the cycle too, but the demos don't use it. Each demo's shared settings start new sessions in Manual mode.

Anthropic's Claude Code extension for VS Code works with the same project files, but the walkthroughs use the CLI because they start agents with command-line options and show costs in the CLI's status line.

### Your Own Repositories

From Demo 2 on, you run `git init` inside the demo folder. That gives the demo a repository of its own, separate from your clone of this webinar repository, so the agents' diffs show only their own work, and in Demo 3 only the demo's files go to GitHub. Demo 3 creates a private repository in your GitHub account, and Demo 4 carries on in it. Delete it when you're done if you don't want to keep it.

### Tested Versions

The walkthroughs were written in November 2026 against the current documentation for Claude Code 2.1, GitHub Copilot's cloud agent and code review, the GitHub CLI 2.95, and uv 0.11. The demos' settings, hooks, and instruction files were checked with Claude Code 2.1.318. Use 2.1.277 or later, which reads `AGENTS.md` the way the walkthroughs describe. The agents' interfaces and GitHub's labels change often. If a command, button, or menu doesn't match a walkthrough, check the tool's own documentation for its current name, and carry on with the step.

## The Sample Data

Each demo builds a small SQLite database in its `data` folder the first time the API or the `roombook-facts` server starts. It holds eleven rooms and 27 bookings in late October and early November 2026, across both offices' clock changes. It's never committed. To rebuild it, run this from the demo's folder:

```
uv run python -m roombook.seed --reset
```

The app's clock is pinned to Monday 26 October 2026, so the sample bookings stay in the future whenever you run the demos. `roombook/settings.py` explains how to change it. The tests use their own temporary databases, so running them never touches the sample data.

## The Agents' Answers Will Vary

Claude and Copilot won't write the same code, tests, plans, or reviews for you that they wrote for us, so the walkthroughs tell you what to look for rather than what to expect word for word. Each demo starts from a fixed version of the previous demo's work, so you can pick up at any demo, and the [reference folder](./reference/README.md) holds the finished code. It sits outside the demo folders on purpose, so no agent finds the answer while it's working.

## What the Agents Cost

Every demo spends tokens. Claude Code's usage counts against your Claude plan or your API account, and Copilot's cloud agent and code review use AI Credits from your Copilot plan. Both also run on GitHub Actions, and in a private repository their minutes count against your account's Actions allowance. Demo 2's ledger and Demo 4's last part show you how to see what each step cost.

## Using Another AI Tool

The workflow doesn't depend on these tools. `AGENTS.md` is read by most coding agents, including [Copilot](https://code.visualstudio.com/docs/agent-customization/custom-instructions), [Cursor](https://cursor.com/docs/rules), and OpenAI Codex. The `roombook-facts` server works with any agent that supports MCP, and the spec, the plan, the skills, and the prompts in each walkthrough are plain text you can give to any agent.
