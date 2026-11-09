"""Command-line interface for PantryTrack.

Run ``pantrytrack --help`` (or ``python -m pantrytrack --help``) for usage.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Sequence

from . import __version__, reports
from . import inventory as inv
from .db import connect


# --------------------------------------------------------------------------- #
# Output helpers
# --------------------------------------------------------------------------- #
def _table(rows: list[dict], columns: list[str]) -> str:
    if not rows:
        return "(nothing to show)"
    widths = {c: max(len(c), *(len(_fmt(r[c])) for r in rows)) for c in columns}
    line = "  ".join(c.upper().ljust(widths[c]) for c in columns)
    sep = "  ".join("-" * widths[c] for c in columns)
    body = ["  ".join(_fmt(r[c]).ljust(widths[c]) for c in columns) for r in rows]
    return "\n".join([line, sep, *body])


def _fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".") if value % 1 else f"{value:,.0f}"
    return str(value)


def _item_rows(items: list[inv.Item]) -> list[dict]:
    return [
        {
            "name": i.name,
            "category": i.category,
            "qty": i.quantity,
            "unit": i.unit,
            "reorder_at": i.reorder_level,
            "value_eur": i.stock_value,
            "status": "LOW" if i.is_low and i.reorder_level > 0 else "ok",
        }
        for i in items
    ]


# --------------------------------------------------------------------------- #
# Command handlers
# --------------------------------------------------------------------------- #
def cmd_init(conn, args):
    print(f"Database ready: {args.db or 'pantrytrack.db'}")


def cmd_add(conn, args):
    item = inv.add_item(
        conn,
        args.name,
        args.unit,
        category=args.category,
        quantity=args.qty,
        reorder_level=args.reorder_level,
        unit_cost=args.cost,
        supplier=args.supplier,
    )
    print(f"Added '{item.name}' ({item.quantity:g} {item.unit}).")


def cmd_import(conn, args):
    imported, skipped = inv.import_items_csv(conn, args.csv_file)
    print(f"Imported {imported} item(s).")
    if skipped:
        print(f"Skipped {len(skipped)} existing item(s): {', '.join(skipped)}")


def cmd_list(conn, args):
    items = inv.list_items(conn, category=args.category)
    print(_table(_item_rows(items), ["name", "category", "qty", "unit", "reorder_at", "value_eur", "status"]))
    print(f"\nTotal stock value: €{inv.stock_value(conn):,.2f}")


def cmd_receive(conn, args):
    item = inv.receive(conn, args.name, args.qty, unit_cost=args.cost, note=args.note)
    print(f"Received {args.qty:g} {item.unit} of '{item.name}'. In stock: {item.quantity:g} {item.unit}.")


def cmd_use(conn, args):
    item = inv.use(conn, args.name, args.qty, note=args.note)
    print(f"Used {args.qty:g} {item.unit} of '{item.name}'. In stock: {item.quantity:g} {item.unit}.")
    if item.is_low and item.reorder_level > 0:
        print(f"  ! '{item.name}' is at or below its re-order level ({item.reorder_level:g} {item.unit}).")


def cmd_waste(conn, args):
    item = inv.waste(conn, args.name, args.qty, reason=args.reason)
    print(f"Logged waste: {args.qty:g} {item.unit} of '{item.name}' (€{args.qty * item.unit_cost:,.2f}).")


def cmd_count(conn, args):
    item = inv.adjust(conn, args.name, args.qty, note=args.note)
    print(f"Stock of '{item.name}' set to {item.quantity:g} {item.unit}.")


def cmd_low(conn, args):
    items = inv.low_stock(conn)
    print(_table(_item_rows(items), ["name", "qty", "unit", "reorder_at"]))


def cmd_reorder(conn, args):
    rows = inv.reorder_list(conn, multiplier=args.multiplier)
    cols = ["supplier", "item", "in_stock", "order_qty", "unit", "est_cost"]
    print(_table(rows, cols))
    if rows:
        print(f"\nEstimated order total: €{sum(r['est_cost'] for r in rows):,.2f}")
    if args.out and rows:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols)
            writer.writeheader()
            writer.writerows({c: r[c] for c in cols} for r in rows)
        print(f"Saved order list to {args.out}")


def cmd_report(conn, args):
    df = reports.summary(conn, days=args.days)
    period = f"last {args.days} days" if args.days else "all time"
    print(f"Stock summary ({period})\n")
    print(df.to_string(index=False) if not df.empty else "(no movements yet)")
    reasons = reports.waste_by_reason(conn, days=args.days)
    if not reasons.empty:
        print("\nWaste by reason\n")
        print(reasons.to_string(index=False))
        print(f"\nTotal waste cost: €{reasons['cost'].sum():,.2f}")
    if args.out:
        df.to_csv(args.out, index=False)
        print(f"\nSaved summary to {args.out}")
    if args.chart:
        path = reports.plot_waste(conn, args.chart, days=args.days)
        print(f"Saved chart to {path}")


def cmd_history(conn, args):
    df = reports.movements_df(conn, item=args.name).head(args.limit)
    if df.empty:
        print("(no movements yet)")
        return
    print(df[["date", "item", "kind", "quantity", "unit", "cost", "note"]].fillna("-").to_string(index=False))


# --------------------------------------------------------------------------- #
# Argument parser
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pantrytrack",
        description="Open-source stock and food-waste tracker for small restaurants and cafés.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("--db", help="path to the database file (default: $PANTRYTRACK_DB or ./pantrytrack.db)")
    sub = p.add_subparsers(dest="command", required=True, metavar="COMMAND")

    s = sub.add_parser("init", help="create an empty database")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("add", help="add a new stock item")
    s.add_argument("name")
    s.add_argument("--unit", required=True, help="e.g. kg, l, pcs, box")
    s.add_argument("--category", help="e.g. dairy, produce, dry goods")
    s.add_argument("--qty", type=float, default=0, help="opening quantity")
    s.add_argument("--reorder-level", type=float, default=0, help="warn when stock falls to this level")
    s.add_argument("--cost", type=float, default=0, help="cost per unit in €")
    s.add_argument("--supplier")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("import", help="import items from a CSV file")
    s.add_argument("csv_file")
    s.set_defaults(func=cmd_import)

    s = sub.add_parser("list", help="show all items and their stock")
    s.add_argument("--category")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("receive", help="record a delivery")
    s.add_argument("name")
    s.add_argument("qty", type=float)
    s.add_argument("--cost", type=float, help="new cost per unit in €")
    s.add_argument("--note")
    s.set_defaults(func=cmd_receive)

    s = sub.add_parser("use", help="record stock used in the kitchen")
    s.add_argument("name")
    s.add_argument("qty", type=float)
    s.add_argument("--note")
    s.set_defaults(func=cmd_use)

    s = sub.add_parser("waste", help="record stock thrown away")
    s.add_argument("name")
    s.add_argument("qty", type=float)
    s.add_argument("--reason", help="e.g. expired, spoiled, damaged, overproduction")
    s.set_defaults(func=cmd_waste)

    s = sub.add_parser("count", help="set stock to a physically counted quantity")
    s.add_argument("name")
    s.add_argument("qty", type=float)
    s.add_argument("--note")
    s.set_defaults(func=cmd_count)

    s = sub.add_parser("low-stock", help="items at or below their re-order level")
    s.set_defaults(func=cmd_low)

    s = sub.add_parser("reorder", help="suggested order list grouped by supplier")
    s.add_argument("--multiplier", type=float, default=2.0, help="order up to N x re-order level (default 2)")
    s.add_argument("--out", help="save the list as CSV")
    s.set_defaults(func=cmd_reorder)

    s = sub.add_parser("report", help="usage and waste summary")
    s.add_argument("--days", type=int, default=30, help="period in days (default 30)")
    s.add_argument("--out", help="save the summary as CSV")
    s.add_argument("--chart", help="save a waste-cost bar chart (PNG)")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("history", help="list recent stock movements")
    s.add_argument("name", nargs="?")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_history)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    conn = connect(args.db)
    try:
        args.func(conn, args)
    except (inv.PantryTrackError, ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
