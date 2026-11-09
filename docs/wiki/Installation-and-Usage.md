# Installation and Usage

## 1. Install

```bash
git clone https://github.com/nikolaosmanhss-png/pantrytrack.git
cd pantrytrack
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install .
pantrytrack --version
```

## 2. Set up your items

Either import a CSV (see `examples/sample_items.csv`):

```bash
pantrytrack import my_items.csv
```

or add items one at a time:

```bash
pantrytrack add "Feta cheese" --unit kg --category dairy --qty 6 --reorder-level 2 --cost 8.50 --supplier "Dairy Co"
```

**Tip:** the re-order level is the quantity at which you want to be warned. A good starting point is "what we use in two days".

## 3. Daily routine (2 minutes)

| When | Command |
|---|---|
| A delivery arrives | `pantrytrack receive Milk 12 --cost 1.10` |
| End of service | `pantrytrack use Tomatoes 9` |
| Something is thrown away | `pantrytrack waste Milk 1.5 --reason expired` |
| Before calling suppliers | `pantrytrack reorder --out order.csv` |

## 4. Weekly / monthly

```bash
pantrytrack count "Olive oil" 7.5          # after a physical stock-take
pantrytrack report --days 30 --chart waste.png --out summary.csv
```

The report shows, per item, what was received, used and wasted, the waste cost in euros and the **waste rate** (wasted ÷ (used + wasted)). Items with a high waste rate are being over-ordered or stored badly.

## 5. Several shops

Keep one database per shop:

```bash
pantrytrack --db cafe_centre.db list
set PANTRYTRACK_DB=cafe_port.db   # Windows (export on macOS/Linux)
```

## 6. Modifying PantryTrack

PantryTrack is MIT-licensed, so you may change it for your own business. Common changes:

- **Different currency** – change the `€` symbol in `cli.py` and `reports.py`.
- **New report** – add a function to `reports.py` that returns a pandas DataFrame, then a sub-command in `cli.py`.
- **Web interface** – import `inventory` and `reports` from a Flask or Django app; the logic does not depend on the CLI.

If your change could help others, please open a pull request (see CONTRIBUTING.md).
