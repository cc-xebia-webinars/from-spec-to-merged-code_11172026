# Demo 4: Review, Fix, Merge, and the Bill

In this demo you'll close the loop on GitHub. You'll review the pull request Copilot's cloud agent opened in Demo 3 and merge it, ask Copilot code review to review your feature, and hand one of its findings back to the cloud agent as a fix pull request. While that runs, you'll add up what the whole run cost. Then you'll make the merge decision yourself.

## Before You Start

This demo carries on in the repository you created in Demo 3, because the pull requests and the review live on GitHub. Work in a terminal in your **Demo 3 folder**, on the `feature/weekly-allowance` branch. This folder holds what that branch should look like at the end of Demo 3, so you can compare it with yours, and its 75 tests pass.

You'll need the same tools as in Demo 3:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.11 or later
- [Visual Studio Code](https://code.visualstudio.com/)
- The [Claude Code CLI](https://code.claude.com/docs/en/setup)
- The [GitHub CLI](https://cli.github.com/) 2.88 or later, signed in with `gh auth login`
- A GitHub account with a [Copilot plan that includes the cloud agent and code review](https://docs.github.com/en/copilot/get-started/plans)

Copilot charges code reviews in AI Credits, by the tokens they use, and a review also uses GitHub Actions minutes. Before you start, set your default review effort level to **Lite** in your Copilot settings, under **Code review**. The levels are Lite, Balanced (the default), and Max (in preview). Lite costs a fraction of Balanced, and the `gh pr edit` command you'll use to request the review has no option for the level. If you request a review in the browser instead, the pull request's **Reviewers** section lets you pick the level for that review.

List the open pull requests:

```
gh pr list
```

You should see two: Copilot's, for the schedule issue, and your draft, "Weekly booking allowance". Note both numbers; the steps below call them the Copilot PR and the feature PR. If Copilot's title still starts with "[WIP]", it's still working: do Step 1, then go on to Part 2, and come back to its pull request when it's done.

## What's in This Folder

| File | Purpose |
|------|---------|
| `roombook/` | The Roombook API with the weekly allowance, as your branch should be after Demo 3 |
| `tests/` | 75 tests, including the acceptance tests and the test for pending bookings |
| `.github/` | The CI workflow, the cloud agent's setup steps, and the review instructions |

## Presentation Trail

### Part 1: Start the review, then the cloud agent's pull request

#### Step 1: Ask Copilot to review the feature

A review takes a few minutes, so start it first and let it run while you work on Copilot's pull request. Mark your feature pull request as ready:

```
gh pr ready <feature-pr>
```

Then request a review from Copilot:

```
gh pr edit <feature-pr> --add-reviewer "@copilot"
```

Copilot code review is an agent too. It reads the repository for context, not just the diff, and it follows `.github/instructions/review.instructions.md`. Open that file: it tells the reviewer to check the change against its spec, flag anything the spec doesn't ask for, and watch for weeks worked out in UTC.

#### Step 2: Open Copilot's pull request

Open Copilot's pull request in your browser, using its number:

```
gh pr view <copilot-pr> --web
```

#### Step 3: Read the session

Select **View session**. The log shows what the agent did and why: the files it read, including `AGENTS.md`, the commands it ran, and the tests. The overview shows how long it ran and how many tokens it used. Check how it got `uv`, and that it ran the tests before it said it was done.

#### Step 4: Let CI run

Copilot's pushes don't start any workflows until someone with write access to the repository approves them, so an agent can't run code in your CI on its own. On the pull request, select **Approve and run workflows**. Then watch the checks:

```
gh pr checks <copilot-pr> --watch
```

#### Step 5: Review it and merge it

Open **Files changed**. The issue asked for a change to `roombook/schedule.py`, the `ScheduleEntry` model, and a new test file, and nothing else. Check that the new test asserts Ava Thompson's name on the Launch rehearsal, as the issue's first criterion says.

The cloud agent can't mark its own pull request as ready, approve it, or merge it. Those are your decisions. Mark it as ready:

```
gh pr ready <copilot-pr>
```

Then merge it:

```
gh pr merge <copilot-pr> --squash --delete-branch
```

### Part 2: Agentic review on the feature

#### Step 6: Read the review

Open the pull request in your browser:

```
gh pr view <feature-pr> --web
```

Read each comment. Copilot's review is a suggestion, not a verdict. By default it's left as a comment, so it doesn't count as an approval. An administrator can turn on Copilot approvals, which do count, but this repository doesn't use them. For each comment, decide whether you agree. If you don't, reply with your reason and resolve the conversation.

#### Step 7: Hand one fix to the cloud agent

Pick a comment you agree with, select **Fix with Copilot**, and choose to open a new pull request against your branch. The cloud agent makes the change in its own pull request, so you review the fix on its own rather than finding it mixed into your branch.

If no comment is worth fixing, add this comment to the pull request instead, and the cloud agent does the same:

```text
@copilot Open a pull request against this branch that expands the docstring of db.person_bookings to say which booking statuses count towards the allowance, and why, quoting the spec.
```

The fix takes a few minutes. Carry on with Part 3 while it runs.

### Part 3: What the whole run cost

#### Step 8: The Claude side

In your Demo 3 folder, report what each Claude agent cost there:

```
uv run python .claude/hooks/cost_ledger.py --report
```

Run the same command in your Demo 2 folder to see the agent team's build. Remember that these are estimates at API list prices.

#### Step 9: The GitHub side

Copilot charges in AI Credits. One credit is one US cent, charged at each model's token rates. If you pay for Copilot Pro or Pro+ annually, your plan still counts premium requests instead. On a personal plan, open [your billing settings](https://github.com/settings/billing) and select **AI usage**, which breaks your credits down by model. On Copilot Business or Enterprise, your Copilot settings show a **Usage this cycle** card instead. The cloud agent's session overview from Step 3 shows its tokens, and the review's cost depends on the effort level you chose. Both also used GitHub Actions minutes.

Add it up: the agent team, the loop and the verifier, the cloud agent's two sessions, and the review. That's what it cost to take one feature from spec to merge, and it's the number to compare with what the same work costs a person.

### Part 4: The merge decision

#### Step 10: Review and merge the fix

List the pull requests again:

```
gh pr list
```

Find the cloud agent's fix pull request. Its base branch is `feature/weekly-allowance`. If its title still starts with "[WIP]", it's still working, so carry on with Step 11 without it and come back to it later.

Otherwise, open it and read the diff. You don't need to wait for its own checks: merging it into your branch starts a new CI run on the feature pull request, and Step 11 checks that run. If it does only what the comment asked, mark it as ready:

```
gh pr ready <fix-pr>
```

Then merge it into your branch:

```
gh pr merge <fix-pr> --squash --delete-branch
```

#### Step 11: Decide on the feature

An agent could do every step up to here, but merging is where a person signs off. Go through the checklist before you merge:

- CI passes on the feature pull request. Check it with `gh pr checks <feature-pr> --watch`, which waits for any run that's still going.
- Every acceptance criterion in the spec has a test, and it passes.
- Every finding from the verifier is fixed.
- Every review comment is fixed, or answered and resolved.
- The diff changes nothing the spec doesn't ask for. List the files with `gh pr diff <feature-pr> --name-only`.
- What the run cost is acceptable for what it delivered.
- You understand the change well enough to support it when it breaks.

When every box is ticked, merge it:

```
gh pr merge <feature-pr> --squash --delete-branch
```

#### Step 12: Pull main and run the tests

Switch to `main`:

```
git switch main
```

Pull both merges:

```
git pull
```

Sync the dependencies, in case they changed:

```
uv sync
```

Then run the tests:

```
uv run pytest
```

Every test passes: the 75 from your branch, plus the tests Copilot added for the schedule change and any the fix pull request added. To compare with a finished version, see the [reference folder](../reference/README.md), whose 76 tests include one for the schedule change.

## What You Saw

- A cloud agent's pull request gets the same review as anyone's, and the platform keeps the key steps with people: running workflows, marking it as ready, approving it, and merging it.
- Agentic code review reads the repository and follows instructions you write, and its findings are suggestions for you to judge.
- A review finding can go back to the cloud agent as its own small fix pull request, so every change stays reviewable.
- Token-based billing makes each agent's cost visible, and adding it up is part of deciding where agents are worth it.
- The merge decision is a checklist a person works through, with evidence from CI, the verifier, and the review.
