# Development Workflow

## Tools

| Need | Tool |
|---|---|
| Version control | Git + GitHub |
| Bug & feature tracking | GitHub Issues (with templates and labels) |
| Project management | GitHub Projects (Kanban board: To do / In progress / Done) and Milestones |
| Code review | GitHub Pull Requests |
| Continuous integration | GitHub Actions (tests on Python 3.10–3.13 for every push and PR) |
| Documentation | README + GitHub Wiki (this wiki) |
| Communication | GitHub Discussions / issue comments |
| Editor | Visual Studio Code |

## Branching model

- `main` is always releasable and protected (no direct pushes; PR + green CI required).
- One branch per issue: `feature/<issue>-<short-name>`, `fix/...`, `docs/...`.
- Branches are merged with a pull request and deleted afterwards.

## From idea to release

1. An idea or bug is opened as an **issue** and labelled.
2. The issue is added to the **project board** and a **milestone** (e.g. v0.1.0).
3. A contributor is assigned and creates a branch.
4. Work is pushed and a **pull request** is opened (`Closes #N`).
5. **CI** runs the tests automatically; a maintainer reviews.
6. The PR is merged, the issue closes automatically and the card moves to *Done*.
7. When the milestone is complete, a **release** is tagged (e.g. `v0.1.0`) and the CHANGELOG is updated.

## Decision making

- Small changes: decided in the pull request review.
- Larger changes: discussed in an issue first; **lazy consensus** (accepted if no objection within 7 days).
- Disagreements: the project lead (maintainer) decides and documents the reason in the issue.

## Quality gates

- All tests pass (`pytest`).
- Lint clean (`ruff check`).
- New behaviour is covered by tests.
- User-facing changes are documented in README and CHANGELOG.
