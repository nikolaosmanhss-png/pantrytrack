# PantryTrack

[![CI](https://github.com/nikolaosmanhss-png/pantrytrack/actions/workflows/ci.yml/badge.svg)](https://github.com/nikolaosmanhss-png/pantrytrack/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**Open-source stock and food-waste tracker for small restaurants, cafés and bakeries.**

PantryTrack is a free command-line tool that helps a small food business answer three questions every day:

1. **What do we have?** – live stock levels and stock value per item.
2. **What do we need to order?** – low-stock alerts and an order list grouped by supplier.
3. **What are we throwing away?** – waste logging with reasons, cost and a chart of the worst items.

All data stays in one local SQLite file. No server, no subscription, no account.

---

## Why this project exists

Small hospitality businesses usually track stock on paper or in spreadsheets. This leads to two expensive problems: **stock-outs** (dishes that cannot be served) and **food waste** (products that expire because too much was ordered). Commercial inventory platforms solve this, but they are subscription-based and designed for chains, so they are often too costly and too complex for a single café or taverna.

PantryTrack is a small, transparent alternative that any business can use, inspect and adapt for free. See the [project wiki](../../wiki) for the full problem statement, design decisions and project log.

## Features

| Feature | Command |
|---|---|
| Add items one by one or import them from CSV | `add`, `import` |
| Record deliveries, kitchen usage and waste (with reason) | `receive`, `use`, `waste` |
| Stock-take correction after a physical count | `count` |
| Live stock list with total stock value | `list` |
| Low-stock alerts | `low-stock` |
| Suggested order list per supplier, exportable to CSV | `reorder` |
| Usage and waste report (pandas) and waste-cost chart (matplotlib) | `report` |
| Movement history per item | `history` |

![Example waste chart](docs/images/waste-chart.png)

## Installation

Requirements: **Python 3.10 or newer**.

```bash
git clone https://github.com/nikolaosmanhss-png/pantrytrack.git
cd pantrytrack
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install .
```

Check that it works:

```bash
pantrytrack --version
```

## Quick start

```bash
# 1. Load the example items (14 typical café products)
pantrytrack import examples/sample_items.csv

# 2. Record a normal day
pantrytrack use Tomatoes 9
pantrytrack waste Tomatoes 2 --reason spoiled
pantrytrack use Milk 7
pantrytrack receive Tomatoes 10 --cost 1.75 --note "Green Market delivery"

# 3. See where you stand
pantrytrack list
pantrytrack low-stock
pantrytrack reorder --out order.csv
pantrytrack report --days 30 --chart waste.png
```

Example output of `pantrytrack reorder`:

```
SUPPLIER       ITEM            IN_STOCK  ORDER_QTY  UNIT  EST_COST
-------------  --------------  --------  ---------  ----  --------
Bean Roasters  Coffee beans    2         2          kg    36
Butcher Bros   Chicken breast  2.2       3.8        kg    27.36
Dairy Co       Milk            3.5       8.5        l     9.35

Estimated order total: €72.71
```

By default the database is `pantrytrack.db` in the current folder. Use `--db path/to/file.db` or set the `PANTRYTRACK_DB` environment variable to keep one database per shop.

Run `pantrytrack COMMAND --help` for all options of a command.

## CSV import format

```csv
name,unit,category,quantity,reorder_level,unit_cost,supplier
Feta cheese,kg,dairy,6,2,8.50,Dairy Co
```

Only `name` and `unit` are required. Items that already exist are skipped.

## Using PantryTrack as a library

```python
from pantrytrack.db import connect
from pantrytrack import inventory, reports

conn = connect("shop.db")
inventory.add_item(conn, "Feta", "kg", quantity=5, reorder_level=2, unit_cost=8.5)
inventory.waste(conn, "Feta", 1, reason="expired")
print(reports.summary(conn, days=7))
```

## Project structure

```
src/pantrytrack/
├── db.py          # SQLite connection and schema
├── inventory.py   # items, stock movements, low-stock and re-order logic
├── reports.py     # pandas summaries and matplotlib charts
└── cli.py         # command-line interface (argparse)
tests/             # pytest test-suite (runs in GitHub Actions on every push)
examples/          # sample data
docs/wiki/         # source of the GitHub wiki pages
```

## Built with

- [Python](https://www.python.org/) and its built-in [SQLite](https://www.sqlite.org/) module
- [pandas](https://pandas.pydata.org/) – data analysis for reports
- [Matplotlib](https://matplotlib.org/) – charts
- [pytest](https://pytest.org/) – testing

## Roadmap

- [ ] Expiry dates per delivery batch and "use first" (FIFO) warnings
- [ ] Simple web dashboard (Flask)
- [ ] Greek translation of the CLI messages
- [ ] Recipe costing (ingredients per dish)

Ideas and votes are welcome in [Issues](../../issues).

## Contributing

Contributions of any size are welcome – bug reports, documentation, translations and code. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md) before opening a pull request.

## License

PantryTrack is released under the [MIT License](LICENSE). You may use, modify and distribute it, including commercially, as long as the copyright notice is kept.

## Author

Nikolaos Manis – SWE6005 Open Source Software Development, New York College (2025/2026).
