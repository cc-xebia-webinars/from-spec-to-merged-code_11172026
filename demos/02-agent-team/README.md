# Demo 2: An Agent Team Builds the Feature

In this demo a small team of agents builds the weekly allowance from Demo 1's spec and plan. A coordinator splits the work and never edits a file, implementors each build one slice, and a verifier checks the result. Each role has only the tools it needs. You'll watch two implementors work at the same time, then see what each agent cost.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/)
- The [Claude Code CLI](https://code.claude.com/docs/en/setup), signed in with a Claude Pro, Max, Ultra, Team, or Enterprise plan or a Claude Console account

Open this folder as its own VS Code window, trust it if VS Code asks, and open a terminal. Install the dependencies:

```
uv sync
```

The team works in git, so you can see exactly what it changed, and the hook that protects tests only protects files git tracks. Make this folder a repository of its own:

```
git init -b main
```

Then commit the starting point:

```
git add .
```

```
git commit -m "Roombook with the weekly allowance spec and plan"
```

On Windows, git may warn that line endings will be converted. Those warnings are harmless. Run the tests:

```
uv run pytest
```

65 pass and 4 fail. The failures are the acceptance tests for criteria 1, 3, 6, and 7, which the team is about to make pass.

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/` | The Roombook API, before the feature |
| `docs/specs/weekly-allowance.md` | The spec from Demo 1 |
| `docs/plans/weekly-allowance.md` | The reviewed plan from Demo 1, split into three slices |
| `tests/acceptance/test_weekly_allowance.py` | One acceptance test per criterion, written from the spec |
| `.claude/agents/` | The three roles: `coordinator`, `implementor`, and `verifier` |
| `.claude/skills/verify-against-spec/` | The checklist the verifier works through |
| `.claude/hooks/cost_ledger.py` | The hook that records what each agent costs |
| `.claude/statusline.py` | The status line under the prompt |
| `.claude/settings.json` | Shared permissions, the status line, and the hooks |

## Presentation Trail

### Part 1: The team and its permissions

#### Step 1: Read the coordinator

Open `.claude/agents/coordinator.md`. An agent file has two parts: frontmatter that sets what the agent can do, and a body that becomes its instructions.

- `tools` lists everything the coordinator can use. `Agent(implementor, verifier)` lets it start those two agents and no others. There's no `Edit` or `Write`, so it can't change a file itself; it can only delegate.
- `model: opus` puts the planning and judgment on the most capable model.
- The body tells it how to brief an implementor, when to run slices at the same time, and when to stop and ask you.

#### Step 2: Read the implementor and the verifier

Open `.claude/agents/implementor.md`. It can edit files, runs on `sonnet`, which costs less, and has `permissionMode: acceptEdits`, so its edits don't stop for approval. That mode also runs simple file commands, such as `mkdir`, `mv`, and `rm`, inside the project without asking, while other commands outside the allow list still ask. The hook still blocks edits to existing tests, but it only watches the edit tools, not the shell, which is one reason you run the tests and read the diff yourself in Step 8. `maxTurns` stops a run that's going nowhere.

Then open `.claude/agents/verifier.md`. `disallowedTools` takes away `Edit` and `Write`, so it can only read and run checks. `skills` loads the `verify-against-spec` checklist into its context when it starts. Open `.claude/skills/verify-against-spec/SKILL.md` to see that checklist: the tests, every criterion, every rule, every constraint, and anything out of scope.

All three agents can call the `roombook-facts` tools, listed in `tools` as `mcp__roombook-facts__*`, so they all check facts against the same source.

#### Step 3: Read the plan

Open `docs/plans/weekly-allowance.md`. Slice A adds `week_bounds`, slice B adds the allowance check, and slice C wires it into bookings, moves, and series. The plan fixes the signature of `week_bounds`, so slices A and B can be built at the same time. Slice C needs both.

#### Step 4: Read how costs are tracked

Open `.claude/settings.json` and find `statusLine` and the `SubagentStop` and `Stop` hooks. Then open `.claude/hooks/cost_ledger.py`. Claude Code shows a session's total cost, but not what each agent cost. Every agent's transcript records its model and the tokens each response used, so when an agent finishes, the hook reads its transcript, prices the tokens, and adds a line to `.claude/cost-ledger.jsonl`.

### Part 2: Run the team

#### Step 5: Start the coordinator

Start Claude Code with the coordinator as the main agent:

```
claude --agent coordinator
```

If Claude asks whether to use the `roombook-facts` server from `.mcp.json`, choose to use it, as you did in Demo 1. Each project folder asks once, and every agent on the team needs it.

The header shows `@coordinator`, and the status line under the prompt shows the agent, the model, how full the context is, and the session's cost so far. Send this prompt:

```text
Build the feature in docs/specs/weekly-allowance.md, following docs/plans/weekly-allowance.md.
```

#### Step 6: Watch the slices run

The coordinator reads the spec and the plan, runs the tests, and briefs two implementors for slices A and B. They work at the same time, and the agent panel below the prompt shows each one while it runs. When both are done, it starts slice C, and then the verifier.

While it works, read one of the briefs the coordinator wrote. A subagent starts with none of the conversation, so the brief has to carry everything: the files, the signatures, the tests to pass, and the constraints. If a command needs your approval, read it before you allow it.

#### Step 7: Read the verifier's report

The verifier finishes with a table of findings and a verdict. If it finds something, the coordinator sends it back to an implementor, at most twice. The agents won't write the same code for you that they wrote for us, so read the findings rather than expecting a particular result.

### Part 3: Check the work and the bill

#### Step 8: Run the tests and read the diff

In a second terminal, run the tests yourself:

```
uv run pytest
```

Every test should pass, including the 62 that were there before and the 7 acceptance tests. Then see what the team changed:

```
git status
```

Open the **Source Control** view and read the diff. Check that `tests/acceptance/` didn't change, that there's a new `roombook/allowance.py`, and that nothing outside the plan's files changed.

#### Step 9: See what each agent cost

In the Claude terminal, see the session's total:

```text
/usage
```

Then, in the second terminal, see the cost per agent:

```
uv run python .claude/hooks/cost_ledger.py --report
```

There's a row for the coordinator and one for each kind of subagent, with its runs, tokens, and estimated cost. The implementors usually read and write the most tokens, which is why they run on a cheaper model. The figures are estimates at API list prices. On a Claude subscription they show what the work would have cost at API rates, not what you're billed.

## What You Saw

- Each role gets only the tools it needs. The coordinator can't edit, the implementors can edit without stopping but can't edit existing tests, and the verifier can only read and run checks.
- A plan that fixes the interfaces between slices lets independent slices run in parallel, and the coordinator's briefs carry everything a subagent knows.
- Per-agent costs come from the transcripts' token counts. Putting the cheaper model on the heaviest work is the main lever on the bill.
- You still run the tests and read the diff yourself, because the team's report, like any agent's, is a claim to check.
