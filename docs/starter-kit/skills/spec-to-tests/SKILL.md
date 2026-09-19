---
description: Turn a spec's numbered acceptance criteria into failing tests, one per criterion, before any code is written. Use when asked to make a spec executable or to write acceptance tests from a spec.
argument-hint: <spec name>
---

# Turn a spec into failing acceptance tests

The spec is `docs/specs/$ARGUMENTS.md`. If no spec name was given, list the files in `docs/specs/` and ask which one to use.

The tests you write become the definition of done for every agent that builds the feature, so they have to say exactly what the spec says, no more and no less.

1. Read the spec, including the rules that explain the criteria. If the project has an MCP server with the spec's criteria, get them from there, so every agent works from the same list.
2. Check every fact a criterion relies on against the real data or environment, using the project's tools. If the data doesn't match what the spec says, stop and report the mismatch instead of writing a test around it.
3. Write the tests to `tests/acceptance/`:
   - One test per criterion, named after the criterion's number and what it checks, with a docstring that quotes the criterion.
   - Use the project's existing test fixtures, and call the code the way a user would.
   - Copy expected values from the spec. Never work them out yourself.
   - A criterion that's met by running the whole suite, such as "every existing test still passes", doesn't need a test of its own. Mention it in the module docstring.
4. Don't write or change any production code, and don't touch the existing tests.
5. Run the new tests. A test for a criterion that rejects something should fail now. A test for a criterion that accepts something may already pass; it's there to catch an implementation that goes too far. A failure caused by the test itself is a bug to fix now.
6. Finish with a table of criterion, test name, and whether the test fails or passes today, and why.
