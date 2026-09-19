---
description: Check a change against its written spec, rule by rule, and report scope creep, broken constraints, and drift that passing tests don't catch. Use when asked to verify, review, or sign off a change against a spec.
argument-hint: <spec name>
---

# Verify a change against its spec

The spec is `docs/specs/$ARGUMENTS.md`. If no spec was named, use the one the change is for, and say which one you picked.

Work out what changed first. Compare the branch with the main branch using `git diff main...HEAD`, plus any uncommitted changes from `git diff`. Read every changed file in full, not only the diff.

Then go through the checklist. Each item needs a verdict and evidence.

1. **The tests.** Run them. Note any failures, and check that no existing test was changed or deleted.
2. **Every acceptance criterion.** Find the test that checks each one, and read it to confirm it asserts what the criterion says, not something close to it.
3. **Every rule in the spec.** Read the rules sentence by sentence and find the code that implements each sentence. Rules with no acceptance criterion are where drift hides, so give them the most attention. Check the details: which states count, which time zone a boundary uses, whether a limit is inclusive.
4. **The constraints.** Check each one against the diff, including the dependency files, the settings, and the routes or public interfaces.
5. **Out of scope.** Anything the change adds that the spec doesn't ask for is scope creep, even when it works and has tests. List each addition.
6. **Ground truth.** Where the code or the tests rely on real data or the environment, check them with the project's tools.

Report a table with one row per finding: severity (blocker, should fix, or note), what's wrong, the evidence (file and line, and the spec sentence), and how a person can see it for themselves. Then give one line for your overall verdict: ready to merge, or not yet. Don't change any files.
