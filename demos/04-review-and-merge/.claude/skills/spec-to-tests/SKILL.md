---
description: Turn a spec's numbered acceptance criteria into failing pytest tests, one per criterion, before any code is written. Use when asked to make a spec executable or to write acceptance tests from a spec.
argument-hint: <spec name, such as weekly-allowance>
---

# Turn a spec into failing acceptance tests

The spec is `docs/specs/$ARGUMENTS.md`. If no spec name was given, list the files in `docs/specs/` and ask which one to use.

The tests you write become the definition of done for every agent that builds the feature, so they have to say exactly what the spec says, no more and no less.

1. Get the numbered criteria with the `spec_criteria` tool from the `roombook-facts` MCP server, then read the whole spec, because the rules section explains the criteria.
2. Check every fact a criterion relies on against the sample data, using `list_bookings` and `clock_changes`. If the data doesn't match what the spec says, stop and report the mismatch instead of writing a test around it.
3. Write the tests to `tests/acceptance/test_<spec name with underscores>.py`:
   - One test per criterion, named `test_criterion_<number>_<what it checks>`, with a docstring that quotes the criterion.
   - Use the `client` fixture from `tests/conftest.py`, and call the API the way a person would.
   - Copy expected values, such as status codes, messages, and local times, from the spec. Never work them out yourself.
   - Look up the ids of existing bookings through the API, by room, day, and title, rather than hard-coding them.
   - A criterion that's met by running the whole suite, such as "every existing test still passes", doesn't need a test of its own. Mention it in the module docstring.
4. Don't write or change any production code, and don't touch the existing tests.
5. Run `uv run pytest tests/acceptance -q`. A test for a criterion that rejects something should fail now, because the feature doesn't exist yet. A test for a criterion that accepts something may already pass, because nothing stops it yet; it's there to catch an implementation that goes too far. A failure caused by the test itself, such as a typo, a bad URL, or a missing fixture, is a bug to fix now.
6. Finish with a table of criterion, test name, and whether the test fails or passes today, and why.
