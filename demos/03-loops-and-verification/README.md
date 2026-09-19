# Demo 3: Loops, a Cloud Agent, and a Second Opinion

In this demo two agents work at once. You'll publish Roombook to a private GitHub repository and hand a small issue to GitHub Copilot's cloud agent, which works on it in the cloud and opens a draft pull request. Meanwhile, on your machine, Claude runs a loop that keeps fixing code until every test passes. Then a verifier agent reviews the result against the spec and finds problems that every test passes. You'll fix them, push the branch, and open a draft pull request of your own.

## Before You Start

You'll need these installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/)
- The [Claude Code CLI](https://code.claude.com/docs/en/setup), signed in with a Claude Pro, Max, Ultra, Team, or Enterprise plan or a Claude Console account
- The [GitHub CLI](https://cli.github.com/) 2.88 or later, signed in with `gh auth login`
- A GitHub account with a [Copilot plan that includes the cloud agent](https://docs.github.com/en/copilot/get-started/plans): Copilot Student, Pro, Pro+, Max, Business, or Enterprise. On Business and Enterprise it's on by default, unless an administrator has turned off the **Copilot in the cloud** policy.

Open this folder as its own VS Code window, trust it if VS Code asks, and open a terminal. Install the dependencies:

```
uv sync
```

Then run the tests:

```
uv run pytest
```

65 pass and 4 fail. This folder starts where Demo 2 started, before the feature. The agent team's work is waiting in [`../reference/team-build/`](../reference/README.md) for you to copy in. It's outside this folder, so it doesn't end up in the repository you publish.

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/` | The Roombook API, before the feature |
| `issues/schedule-shows-who-booked.md` | The issue you'll hand to Copilot's cloud agent |
| `.github/workflows/ci.yml` | Runs the tests on every pull request |
| `.github/workflows/copilot-setup-steps.yml` | Installs uv and the dependencies for the cloud agent |
| `.github/instructions/review.instructions.md` | Instructions for Copilot code review, used in Demo 4 |
| `.claude/agents/verifier.md` | The read-only verifier from Demo 2 |
| `docs/specs/weekly-allowance.md` | The spec |

## Presentation Trail

### Part 1: Hand an issue to a cloud agent

#### Step 1: Commit the starting point

Make this folder a repository of its own:

```
git init -b main
```

```
git add .
```

```
git commit -m "Roombook with the weekly allowance spec and plan"
```

On Windows, git may warn that line endings will be converted. Those warnings are harmless.

#### Step 2: Publish a private repository

Create a private repository on GitHub from this folder and push to it. If you already have a repository called `roombook-allowance`, pick another name.

```
gh repo create roombook-allowance --private --source . --push
```

#### Step 3: Read the issue

Open `issues/schedule-shows-who-booked.md`. It's written like a small spec: what to change and why, acceptance criteria, and constraints. A cloud agent can't ask you a question halfway through, so everything it needs has to be in the issue or in `AGENTS.md`.

#### Step 4: Create the issue and assign it to Copilot

Create the issue from the file:

```
gh issue create --title "Show who booked each meeting in the office schedule" --body-file issues/schedule-shows-who-booked.md
```

It's the repository's first issue, so it's number 1. Assign it to Copilot:

```
gh issue edit 1 --add-assignee "@copilot"
```

Copilot reacts to the issue with 👀 and soon opens a draft pull request, usually titled "[WIP]" while it works. The agent reads `AGENTS.md`, makes the change, and runs the tests. If its session runs on GitHub Actions, `.github/workflows/copilot-setup-steps.yml` installs uv and the dependencies first. If it runs in a cloud sandbox, where setup steps don't run, `AGENTS.md` tells it how to install uv itself. You don't need to watch it. Carry on here, and you'll review its pull request in Demo 4. To check on it at any time, list the pull requests:

```
gh pr list
```

### Part 2: The team's first pass

#### Step 5: Copy the team's work onto a branch

Create a branch for the feature:

```
git switch -c feature/weekly-allowance
```

Copy the agent team's first pass, from an earlier run, over the code:

```
uv run python -c "import shutil; shutil.copytree('../reference/team-build', '.', dirs_exist_ok=True)"
```

The team changed the dependencies, so sync them again:

```
uv sync
```

Then run the tests:

```
uv run pytest
```

74 pass and 2 fail: criterion 6, moving a booking, and criterion 7, a series. The team ran out of turns before it wired the allowance into moves and series, which is typical of a first pass from agents. Commit it as it is:

```
git add .
```

```
git commit -m "Weekly allowance: first pass from the agent team"
```

### Part 3: A loop that runs until the tests pass

#### Step 6: Start Claude and let edits through

Start Claude Code:

```
claude
```

If Claude asks whether to use the `roombook-facts` server from `.mcp.json`, choose to use it, as you did in Demo 1. Each project folder asks once.

Press **Shift+Tab** until the mode under the prompt shows **⏵⏵ accept edits on**. In this mode Claude edits files without asking, and it can also run simple file commands, such as `mkdir`, `mv`, and `rm`, inside this folder. `uv run pytest` is on the allow list, and other commands, such as `uv add`, still ask you first, so the loop can run on its own inside the same guardrails. The hook that protects tests only watches Claude's edit tools, not the shell, which is why the goal below also checks that no tracked test file has changed.

#### Step 7: Set a goal

```text
/goal Every test passes when you run uv run pytest, and no test file that git already tracks has changed. Or stop after 15 turns.
```

Setting a goal starts work straight away. After each turn, a small, fast model checks the condition against what Claude has shown in the conversation. If the condition isn't met, Claude starts another turn with the evaluator's reason as guidance. While it runs, the prompt shows that a goal is active.

Watch it run the tests, read the two failures, pass `booked_by` through `move_booking` and `series.create`, and run the tests again. The condition names the check (`uv run pytest`), what mustn't change (tracked test files), and a limit (15 turns), so the loop can't run on forever. To see its progress, turns, and token spend at any point, run `/goal` on its own.

`/goal` is one of three ways to keep Claude working without you. A `Stop` hook in the settings file does the same with a script you write, for checks that must be deterministic, and `/loop` repeats a prompt on a timer instead of toward a condition.

#### Step 8: Commit the loop's work

When the goal is met, every test passes. In a second terminal (select **+** in the terminal panel), commit the work:

```
git add .
```

```
git commit -m "Weekly allowance: moves and series"
```

### Part 4: A second opinion that isn't on the team's side

#### Step 9: Run the verifier

In the Claude terminal, end the session:

```text
/exit
```

Then start the verifier as the main agent, so it starts fresh, with none of the builders' conversation:

```
claude --agent verifier
```

Send this prompt:

```text
Verify the changes on this branch against docs/specs/weekly-allowance.md.
```

The verifier reads the spec, gets the criteria from `roombook-facts`, diffs the branch against `main`, runs the tests, and works through its checklist.

#### Step 10: Read the findings

Every test passes, 76 of them unless the loop added tests of its own, and the verifier should still report three problems. None of them breaks a test:

- **Scope creep.** The team added `GET /people/{name}/allowance` in `roombook/routes/people.py`, with its own tests. It works, but the spec lists "a way to see how many hours someone has left in a week" as out of scope, and its constraints say not to add an endpoint.
- **Drift from the spec.** `person_bookings` in `roombook/db.py` counts only confirmed bookings, but the spec says pending bookings count too. No acceptance criterion mentions pending bookings, so no test caught it. Robert Kim's pending Quarterly business review on 4 November doesn't count towards his allowance.
- **A broken constraint.** `week_bounds` uses `python-dateutil`, a new dependency, and the spec says not to add one.

If the verifier misses one, ask it about that part of the spec. That's also a reason to keep its checklist up to date: each miss is a line to add.

### Part 5: Fix, push, and open a draft pull request

#### Step 11: Fix the findings

End the verifier's session with `/exit`.

Two of the fixes change what the project checks and what it depends on. Those are decisions a person should make, so you'll make them yourself, one now and one once Claude has finished. First, delete the tests for the out-of-scope endpoint:

```
git rm tests/test_people.py
```

Now start a normal session for the code changes:

```
claude
```

Press **Shift+Tab** until the mode shows **⏵⏵ accept edits on**, and send this prompt:

```text
Fix the rest of the verifier's findings, and nothing else. I've already deleted tests/test_people.py, and I'll remove python-dateutil myself once you're done, so don't change pyproject.toml or uv.lock. Remove the GET /people/{name}/allowance endpoint, because the spec puts it out of scope. Count pending bookings towards the allowance as well as confirmed ones, and add a test in a new file, tests/test_allowance.py, showing that Robert Kim's pending Quarterly business review on 4 November counts. Rewrite timeutils.week_bounds with the standard library, the same way day_bounds works.
```

Claude makes the changes without stopping, and runs the tests when it's done.

#### Step 12: Remove the dependency and run the tests

When Claude has finished, end its session:

```text
/exit
```

Now that nothing should need `python-dateutil`, remove it:

```
uv remove python-dateutil
```

Then run the tests. With the package gone, a clean run also shows that nothing still imports it:

```
uv run pytest
```

Every test passes. If Claude added only the test you asked for, there are 75: the 76 from before, less the two tests for the endpoint you removed, plus the new test for pending bookings.

#### Step 13: Push and open a draft pull request

Commit the fixes:

```
git add .
```

```
git commit -m "Weekly allowance: fix the verifier's findings"
```

Push the branch. Claude can't do this, because the settings deny `git push`:

```
git push -u origin feature/weekly-allowance
```

Open a draft pull request:

```
gh pr create --draft --title "Weekly booking allowance" --body "Implements docs/specs/weekly-allowance.md, checked against the spec by the verifier agent."
```

Your branch should now match the code in [Demo 4's folder](../04-review-and-merge/README.md), apart from `pyproject.toml` and `uv.lock`, which name each folder as a project of its own. Demo 4 carries on in this folder and this repository.

## What You Saw

- A cloud agent works an issue on its own and opens a draft pull request, so the issue has to say everything it needs to know.
- `/goal` keeps Claude working until a condition holds. A good condition names the check, what mustn't change, and when to give up.
- A verifier with no stake in the build, and a checklist that reads the whole spec, finds scope creep and drift that passing tests can't.
- Risky steps, such as deleting a test, removing a dependency, and pushing, stay with a person.
