# Spec: <Feature Name>

## Goal

<Who needs this and why, in two or three sentences. The why helps an agent make the small decisions the spec doesn't cover.>

## Context

- <The files, functions, or patterns to build on, so no agent writes a second version of something that already exists.>
- <Anything about the domain that's easy to get wrong, such as time zones, currencies, or permissions.>
- <Where agents can check facts, such as an MCP server, rather than working them out by hand.>

## The Rule

- <The behavior, stated precisely: what counts, what doesn't, where the boundaries are, and whether a limit is inclusive.>
- <What a user sees when the rule says no, word for word, including the status code.>

## Constraints

- <Where the new code should live.>
- Don't add a dependency, a setting, or an endpoint.
- Don't change <the existing rules, checks, or tests that must stay as they are>.

## Acceptance Criteria

1. <A specific, checkable example with real values from your data, such as "a booking that brings Ava's week to exactly 6 hours is accepted".>
2. <One criterion for each way the rule says no, and one for each edge, such as a clock change or an empty input.>
3. Every existing test still passes, unchanged, and each criterion above has a test.

## Out of Scope

- <What not to build, even if it would be easy, so no agent builds it.>
