# Architecture

## Overview

```
          ┌──────────────┐
 user ──▶ │   cli.py     │  argparse: parses commands, prints tables
          └──────┬───────┘
                 │
     ┌───────────┴────────────┐
     ▼                        ▼
┌──────────────┐       ┌──────────────┐
│ inventory.py │       │  reports.py  │  pandas + Matplotlib
│ business     │       │  summaries,  │
│ rules        │       │  charts      │
└──────┬───────┘       └──────┬───────┘
       └──────────┬───────────┘
                  ▼
           ┌─────────────┐
           │   db.py     │  sqlite3 (Python standard library)
           └─────────────┘
```

The CLI contains **no business logic**. This means the same functions can later be reused by a web or mobile front-end.

## Database schema

**items**

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | primary key |
| name | TEXT | unique, case-insensitive |
| category | TEXT | optional |
| unit | TEXT | kg, l, pcs, box... |
| quantity | REAL | current stock, never negative (CHECK constraint) |
| reorder_level | REAL | warning threshold |
| unit_cost | REAL | latest cost per unit (€) |
| supplier | TEXT | optional |
| created_at | TEXT | ISO-8601 UTC |

**movements** – every change in stock is stored as a row (an *event log*)

| Column | Type | Notes |
|---|---|---|
| id | INTEGER | primary key |
| item_id | INTEGER | foreign key → items (cascade delete) |
| kind | TEXT | `in`, `use`, `waste`, `adjust` |
| quantity | REAL | amount moved |
| unit_cost | REAL | cost at the time of the movement |
| note | TEXT | reason for waste, delivery note... |
| created_at | TEXT | ISO-8601 UTC |

## Key design decisions

| Decision | Reason |
|---|---|
| SQLite instead of a database server | Zero installation for non-technical users; one file is easy to back up |
| Store every movement, not only the current quantity | Allows history, waste analysis and auditing |
| Movement + quantity update in one transaction | Stock and history can never disagree |
| Cost saved on each movement | Waste cost stays correct when prices change later |
| pandas for reports | Pivot tables and grouping in a few lines; well-known library contributors already understand |
| Matplotlib with the `Agg` backend | Charts work on servers and in CI where there is no screen |
| `src/` layout and `pyproject.toml` | Modern Python packaging; `pip install .` creates the `pantrytrack` command |
