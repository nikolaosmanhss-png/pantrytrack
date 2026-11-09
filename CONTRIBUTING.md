# Contributing to PantryTrack

Thank you for considering a contribution! PantryTrack is a small project, so every bug report, idea, translation or pull request makes a real difference.

By taking part you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a bug** – open an issue using the *Bug report* template.
- **Suggest a feature** – open an issue using the *Feature request* template. Describe the business problem first, then the solution.
- **Improve documentation** – README, wiki pages and code comments.
- **Write code** – pick an issue labelled `good first issue` or `help wanted`.
- **Share real-world feedback** – if you run a café or restaurant, tell us what is missing.

## Before you start

1. Search the [existing issues](../../issues) to avoid duplicates.
2. For anything bigger than a small fix, **open an issue first** and wait for a maintainer to agree on the approach. This avoids wasted work.
3. Comment on the issue to say you are working on it, so it can be assigned to you.

## Development setup

```bash
git clone https://github.com/<your-username>/pantrytrack.git
cd pantrytrack
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest                           # all tests must pass
```

## Workflow

We use the **fork-and-pull-request** model with a protected `main` branch.

1. Fork the repository and clone your fork.
2. Create a branch from `main` named after the issue:
   - `feature/12-expiry-dates`
   - `fix/15-negative-stock`
   - `docs/18-install-guide`
3. Make small, focused commits.
4. Add or update tests for any change in behaviour.
5. Run `pytest` and `ruff check src tests` locally.
6. Push the branch and open a pull request against `main`, filling in the PR template and linking the issue (`Closes #12`).

## Commit messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) style:

```
feat: add expiry date to deliveries
fix: prevent negative stock on waste
docs: explain CSV import format
test: cover reorder list grouping
```

Keep the first line under 72 characters and use the imperative mood ("add", not "added").

## Coding standards

- Python 3.10+, formatted to PEP 8 (checked with `ruff`).
- Business logic belongs in `inventory.py` / `reports.py`; `cli.py` only parses arguments and prints.
- Public functions need a docstring.
- No new runtime dependency without discussion in an issue – the tool must stay easy to install for non-technical users.

## Pull request review and decision making

- Every pull request needs **one approving review** from a maintainer and a **green CI build** before it is merged.
- Maintainers aim to give a first response within **7 days**.
- Decisions follow a **lazy consensus** model: a proposal that receives no objection within 7 days of being discussed in an issue is accepted. If there is disagreement, the project lead makes the final decision and explains it in the issue.
- Changes that affect users (new commands, changed data format) must update the README and the `CHANGELOG.md`.

## Labels

| Label | Meaning |
|---|---|
| `bug` | Something does not work as documented |
| `enhancement` | New feature or improvement |
| `documentation` | Docs only |
| `good first issue` | Small, well-described task for newcomers |
| `help wanted` | Maintainers would welcome outside help |
| `question` | Needs more information |

## Licensing of contributions

PantryTrack is licensed under the [MIT License](LICENSE). By submitting a pull request you agree that your contribution is licensed under the same terms (inbound = outbound). Only submit code that you wrote yourself or that is available under a compatible licence, and mention its source.

## Reporting security issues

Please do **not** open a public issue for security problems. Contact the maintainer privately through GitHub instead.

## Recognition

All contributors are listed in the GitHub *Contributors* graph and thanked in the release notes.
