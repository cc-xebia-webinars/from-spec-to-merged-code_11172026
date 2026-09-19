# Spec-to-Merge Checklist

Use this checklist when you take a feature from a written spec to merged code with a team of coding agents, such as Claude Code's subagents and GitHub Copilot's cloud agent. It follows the same order as the webinar: write the spec, ground the agents, plan, build, loop, verify, review, and decide. The demos in this repository show each check in action.

## Write the Spec

- [ ] The spec says who needs the feature and why, so agents can make the small decisions it doesn't cover.
- [ ] The rule is stated precisely: what counts and what doesn't, where the boundaries are, whether a limit is inclusive, and the exact message a user sees.
- [ ] The constraints rule out the shortcuts an agent might take, such as a new dependency, a new setting, an extra endpoint, or a change to existing tests.
- [ ] The acceptance criteria are numbered, specific examples that use real values from your data, including the edge cases most implementations get wrong.
- [ ] Every rule that matters has a criterion. A rule without one is where an implementation drifts unnoticed.
- [ ] The out-of-scope list names what not to build, even when it would be easy.

## Ground the Agents

- [ ] One short `AGENTS.md` holds the commands, the conventions, and the rules that every agent reads, including agents that run in the cloud.
- [ ] Tool-specific files, such as `CLAUDE.md`, import `AGENTS.md` rather than copy it.
- [ ] Facts that agents would otherwise guess at, such as the data, the environment, or the spec's criteria, come from a tool, such as a read-only MCP server.
- [ ] Repeated workflows, such as turning a spec into tests or verifying a change, are written down once as skills.
- [ ] The acceptance tests are written from the spec before any code, and they're committed, so no agent can quietly change them.

## Plan Before Code

- [ ] An agent plans against the spec in a mode that can't change files, and you read the plan before approving it.
- [ ] The plan splits the work into slices, and names the files and the function signatures of each one.
- [ ] Slices that touch different files and only share signatures are marked as safe to build at the same time.
- [ ] The approved plan is saved in the repository, where the agent team can read it.

## Run the Team

- [ ] Each role gets only the tools it needs. The coordinator can't edit, the implementors can't edit existing tests, and the verifier can only read and run checks.
- [ ] Each role runs on a model chosen for its job, with the cheaper model on the heaviest reading and writing.
- [ ] A coordinator's brief to a subagent carries everything it needs: the slice, the files, the signatures, the tests to pass, and the constraints.
- [ ] Hooks enforce the rules that must always hold, such as protected tests and formatting. An instruction is only a request. You know what each hook can't see, such as a file deleted from the shell, and CI catches it.
- [ ] Commands outside the allow list ask a person, and publishing, such as `git push`, is denied to agents. You know which commands each permission mode runs without asking.

## Loops and Cloud Agents

- [ ] A loop's goal names the check that proves it's done, what mustn't change on the way, and when to give up.
- [ ] A loop runs in a permission mode that lets edits through, and its goal checks what that mode doesn't protect. Claude Code's accept-edits mode, for example, also runs `rm` and `mv` without asking.
- [ ] An issue for a cloud agent reads like a small spec, because the agent can't ask you questions halfway through.
- [ ] The cloud agent's environment can install your tools, and you've checked its session log to make sure it found your instructions.

## Verify

- [ ] A verifier with no stake in the build checks the change against the whole spec, not only the acceptance criteria.
- [ ] The verifier works through a written checklist: the tests, every criterion, every rule, every constraint, and anything out of scope.
- [ ] Every finding has evidence: a file and line, the spec sentence it breaks, and how to see it.
- [ ] Each gap the verifier finds in the tests gets a new test, and each miss becomes a new line in its checklist.

## Review

- [ ] Agent pull requests get the same review and CI as anyone's. A person approves the workflows that run on an agent's pushes.
- [ ] Agentic code review has written instructions that point it at the spec and at your domain's common mistakes.
- [ ] Each review comment is fixed, or answered and resolved. A reviewer's findings are suggestions, not a verdict.
- [ ] A fix handed back to an agent comes back as its own small pull request, so it's reviewed on its own.

## Decide and Merge

- [ ] CI passes, and every acceptance criterion has a passing test.
- [ ] Every finding from the verifier and the review is fixed or deliberately declined.
- [ ] The diff changes nothing the spec doesn't ask for.
- [ ] You understand the change well enough to support it when it breaks.
- [ ] A person merges. No agent approves or merges its own work.

## Cost and Governance

- [ ] You can see what each agent cost, on both the local and the cloud side, and you've added it up for the whole feature.
- [ ] Budgets and limits are set where the tools offer them, such as turn limits on loops and usage limits on accounts.
- [ ] The team has agreed where the autonomy line is: what agents may do on their own, what needs a person's approval, and what only a person does.
- [ ] Agent work is labeled in pull requests, and the setup that keeps agents in line (instructions, skills, hooks, settings, and CI) is reviewed like code.
