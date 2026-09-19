# <Project name>

<One or two sentences: what this project is, who uses it, and anything unusual about it.>

## Commands

- Install dependencies: `<command>`. <If a cloud agent's machine may not have a tool, say how to install it, such as `pipx install uv`.>
- Run the tests: `<command>`
- Format and lint: `<command>`
- Run the app: `<command>`

## How It Fits Together

- <Where the entry point is, and how the code is organized.>
- <The conventions a new teammate would get wrong, such as how times, money, or IDs are stored.>
- <Where the business rules live, and who owns them.>

## Specs and Ground Truth

- Features start as a spec in `docs/specs/`. Its numbered acceptance criteria are the definition of done, and the plan for building it goes in `docs/plans/`.
- Acceptance tests live in `tests/acceptance/`, one per criterion, written from the spec before the code.
- <The MCP server that answers questions about the data, the environment, or the specs, and what to ask it. Agents should ask it rather than work facts out by hand.>

## Rules

- Don't edit an existing test to make code pass. If a test looks wrong, stop and explain why.
- Ask before adding a dependency, a setting, or an endpoint the spec doesn't ask for.
- For existing behavior, expected values in tests come from running the code. For new behavior, they come from the spec. Never work them out by hand.
- Keep each change small, and run the tests after it.
- <Files or folders that are off limits, and why.>
