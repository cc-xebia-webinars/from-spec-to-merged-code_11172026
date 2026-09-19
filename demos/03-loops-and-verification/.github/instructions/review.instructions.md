---
applyTo: "**"
excludeAgent: "cloud-agent"
---

# Reviewing changes to Roombook

- Check each change against its spec in `docs/specs/`, or against the issue it fixes. Read the rules, the constraints, and the out-of-scope list, not only the acceptance criteria.
- Flag anything the spec or issue doesn't ask for, such as a new dependency, setting, or endpoint, even when it works and has tests.
- Times are stored in UTC and sent in office time. Flag any day or week that's worked out in UTC rather than from local midnights.
- Existing tests must not change. New tests go in new files.
- Keep each comment short, say which sentence of the spec or issue it relates to, and suggest the smallest fix.
