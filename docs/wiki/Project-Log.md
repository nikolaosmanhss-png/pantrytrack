# Project Log

A dated record of progress, challenges and how they were solved. Update this page as the project moves forward.

| Date | Activity | Challenge | Solution |
|---|---|---|---|
| 2026-11-09 | Chose the problem: stock and food waste in small food businesses | Many possible ideas; needed one that is useful but small enough for v0.1 | Used own experience in hospitality; limited scope to stock, re-order and waste (requirements R1–R9) |
| 2026-11-09 | Chose licence and business model | GPL vs permissive licence | MIT, so businesses and integrators can adopt it without legal concerns (see [[Licensing and Business Model]]) |
| 2026-11-09 | Created GitHub repository, README, LICENSE, CONTRIBUTING, Code of Conduct, issue/PR templates | Making the project welcoming for newcomers | Templates, `good first issue` labels and a clear workflow in CONTRIBUTING |
| 2026-11-09 | Database design | Keeping stock and history consistent | Event log (`movements`) + quantity update in a single SQLite transaction; CHECK constraint stops negative stock |
| 2026-11-09 | Item names | "Feta" and "feta" were treated as different items | `COLLATE NOCASE` on the name column |
| 2026-11-09 | Rounding bug | Using 0.9 l and then 0.1 l from 1 l of cream crashed: floating-point noise gave -0.00000000000000001 and broke the "no negative stock" rule | Round stock to 6 decimals inside the transaction, tolerance when comparing, and a regression test |
| 2026-11-09 | Reports | Waste cost changed when supplier prices changed | Store unit cost on every movement |
| 2026-11-09 | Charts in CI | Matplotlib needs a display, but GitHub Actions has none | Use the non-interactive `Agg` backend |
| 2026-11-09 | Packaging | `license = "MIT"` in `pyproject.toml` failed with older setuptools | Require `setuptools>=77` in the build system |
| 2026-11-09 | Testing | Tests must not touch real data | pytest fixture with an in-memory SQLite database; 25 tests, CI on 4 Python versions |
| 2026-11-09 | Release v0.1.0 | – | Tagged release and CHANGELOG |

## Next steps

- Expiry dates per batch and FIFO warnings (issue)
- Flask web dashboard (issue)
- Greek translation (issue, `good first issue`)
