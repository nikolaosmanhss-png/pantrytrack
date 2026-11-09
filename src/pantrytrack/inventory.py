"""Core inventory logic: items, stock movements, low-stock and re-order lists."""

from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MOVEMENT_KINDS = ("in", "use", "waste", "adjust")


class PantryTrackError(Exception):
    """Base class for all PantryTrack errors."""


class ItemNotFoundError(PantryTrackError):
    """Raised when an item name does not exist in the inventory."""


class DuplicateItemError(PantryTrackError):
    """Raised when trying to add an item that already exists."""


class InsufficientStockError(PantryTrackError):
    """Raised when more stock is taken out than is available."""


@dataclass(frozen=True)
class Item:
    id: int
    name: str
    category: str | None
    unit: str
    quantity: float
    reorder_level: float
    unit_cost: float
    supplier: str | None

    @property
    def stock_value(self) -> float:
        return round(self.quantity * self.unit_cost, 2)

    @property
    def is_low(self) -> bool:
        return self.quantity <= self.reorder_level


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row_to_item(row: sqlite3.Row) -> Item:
    return Item(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        unit=row["unit"],
        quantity=row["quantity"],
        reorder_level=row["reorder_level"],
        unit_cost=row["unit_cost"],
        supplier=row["supplier"],
    )


def _positive(value: float, field: str) -> float:
    value = float(value)
    if value <= 0:
        raise ValueError(f"{field} must be greater than zero (got {value})")
    return value


def _non_negative(value: float, field: str) -> float:
    value = float(value)
    if value < 0:
        raise ValueError(f"{field} cannot be negative (got {value})")
    return value


# --------------------------------------------------------------------------- #
# Items
# --------------------------------------------------------------------------- #
def add_item(
    conn: sqlite3.Connection,
    name: str,
    unit: str,
    *,
    category: str | None = None,
    quantity: float = 0,
    reorder_level: float = 0,
    unit_cost: float = 0,
    supplier: str | None = None,
) -> Item:
    """Add a new stock item. An opening quantity is recorded as an 'in' movement."""
    name = name.strip()
    if not name:
        raise ValueError("name cannot be empty")
    if not unit.strip():
        raise ValueError("unit cannot be empty")
    quantity = _non_negative(quantity, "quantity")
    reorder_level = _non_negative(reorder_level, "reorder_level")
    unit_cost = _non_negative(unit_cost, "unit_cost")

    try:
        cur = conn.execute(
            """INSERT INTO items (name, category, unit, quantity, reorder_level,
                                  unit_cost, supplier, created_at)
               VALUES (?, ?, ?, 0, ?, ?, ?, ?)""",
            (name, category, unit.strip(), reorder_level, unit_cost, supplier, _now()),
        )
    except sqlite3.IntegrityError as exc:
        raise DuplicateItemError(f"item '{name}' already exists") from exc
    conn.commit()

    if quantity > 0:
        _record(conn, cur.lastrowid, "in", quantity, unit_cost, "opening stock")
    return get_item(conn, name)


def get_item(conn: sqlite3.Connection, name: str) -> Item:
    row = conn.execute("SELECT * FROM items WHERE name = ?", (name.strip(),)).fetchone()
    if row is None:
        raise ItemNotFoundError(f"item '{name}' not found")
    return _row_to_item(row)


def list_items(conn: sqlite3.Connection, category: str | None = None) -> list[Item]:
    if category:
        rows = conn.execute(
            "SELECT * FROM items WHERE category = ? COLLATE NOCASE ORDER BY name",
            (category,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM items ORDER BY category, name").fetchall()
    return [_row_to_item(r) for r in rows]


def remove_item(conn: sqlite3.Connection, name: str) -> None:
    item = get_item(conn, name)
    conn.execute("DELETE FROM items WHERE id = ?", (item.id,))
    conn.commit()


# --------------------------------------------------------------------------- #
# Stock movements
# --------------------------------------------------------------------------- #
def _record(
    conn: sqlite3.Connection,
    item_id: int,
    kind: str,
    quantity: float,
    unit_cost: float,
    note: str | None,
) -> None:
    """Write a movement and update the running quantity in one transaction."""
    if kind not in MOVEMENT_KINDS:
        raise ValueError(f"unknown movement kind '{kind}'")
    delta = quantity if kind in ("in", "adjust") else -quantity
    with conn:
        conn.execute(
            """INSERT INTO movements (item_id, kind, quantity, unit_cost, note, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (item_id, kind, quantity, unit_cost, note, _now()),
        )
        # Round to 6 decimals so float noise (1 - 0.9 - 0.1 = -1e-17) can never
        # break the "quantity >= 0" constraint.
        conn.execute(
            "UPDATE items SET quantity = MAX(ROUND(quantity + ?, 6), 0) WHERE id = ?",
            (delta, item_id),
        )


def receive(
    conn: sqlite3.Connection,
    name: str,
    quantity: float,
    *,
    unit_cost: float | None = None,
    note: str | None = None,
) -> Item:
    """Record a delivery from a supplier. Optionally update the unit cost."""
    quantity = _positive(quantity, "quantity")
    item = get_item(conn, name)
    if unit_cost is not None:
        unit_cost = _non_negative(unit_cost, "unit_cost")
        conn.execute("UPDATE items SET unit_cost = ? WHERE id = ?", (unit_cost, item.id))
    cost = item.unit_cost if unit_cost is None else unit_cost
    _record(conn, item.id, "in", quantity, cost, note)
    return get_item(conn, name)


def _take_out(conn, name, quantity, kind, note) -> Item:
    quantity = _positive(quantity, "quantity")
    item = get_item(conn, name)
    if quantity > item.quantity + 1e-9:
        raise InsufficientStockError(
            f"cannot take {quantity:g} {item.unit} of '{item.name}': "
            f"only {item.quantity:g} {item.unit} in stock"
        )
    _record(conn, item.id, kind, quantity, item.unit_cost, note)
    return get_item(conn, name)


def use(conn: sqlite3.Connection, name: str, quantity: float, *, note: str | None = None) -> Item:
    """Record stock used in production (e.g. in the kitchen)."""
    return _take_out(conn, name, quantity, "use", note)


def waste(conn: sqlite3.Connection, name: str, quantity: float, *, reason: str | None = None) -> Item:
    """Record stock that was thrown away (expired, spoiled, damaged...)."""
    return _take_out(conn, name, quantity, "waste", reason)


def adjust(conn: sqlite3.Connection, name: str, counted: float, *, note: str | None = None) -> Item:
    """Set the stock to a physically counted value (stock-take correction)."""
    counted = _non_negative(counted, "counted")
    item = get_item(conn, name)
    delta = counted - item.quantity
    if abs(delta) < 1e-9:
        return item
    _record(conn, item.id, "adjust", delta, item.unit_cost, note or "stock-take")
    return get_item(conn, name)


# --------------------------------------------------------------------------- #
# Decisions
# --------------------------------------------------------------------------- #
def low_stock(conn: sqlite3.Connection) -> list[Item]:
    """Items at or below their re-order level."""
    return [i for i in list_items(conn) if i.is_low and i.reorder_level > 0]


def reorder_list(conn: sqlite3.Connection, multiplier: float = 2.0) -> list[dict]:
    """Suggest how much to order so that stock returns to ``multiplier`` x re-order level.

    The result is grouped by supplier so that one order can be sent per supplier.
    """
    multiplier = _positive(multiplier, "multiplier")
    suggestions = []
    for item in low_stock(conn):
        target = item.reorder_level * multiplier
        order_qty = round(max(target - item.quantity, 0), 2)
        if order_qty <= 0:
            continue
        suggestions.append(
            {
                "supplier": item.supplier or "(no supplier)",
                "item": item.name,
                "unit": item.unit,
                "in_stock": item.quantity,
                "order_qty": order_qty,
                "est_cost": round(order_qty * item.unit_cost, 2),
            }
        )
    return sorted(suggestions, key=lambda s: (s["supplier"], s["item"]))


def stock_value(conn: sqlite3.Connection) -> float:
    return round(sum(i.stock_value for i in list_items(conn)), 2)


# --------------------------------------------------------------------------- #
# CSV import
# --------------------------------------------------------------------------- #
CSV_COLUMNS = ("name", "unit", "category", "quantity", "reorder_level", "unit_cost", "supplier")


def import_items_csv(conn: sqlite3.Connection, path: str | Path) -> tuple[int, list[str]]:
    """Import items from a CSV file. Returns (number imported, list of skipped names)."""
    imported, skipped = 0, []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = {"name", "unit"} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required column(s): {', '.join(sorted(missing))}")
        for row in reader:
            try:
                add_item(
                    conn,
                    row["name"],
                    row["unit"],
                    category=row.get("category") or None,
                    quantity=float(row.get("quantity") or 0),
                    reorder_level=float(row.get("reorder_level") or 0),
                    unit_cost=float(row.get("unit_cost") or 0),
                    supplier=row.get("supplier") or None,
                )
                imported += 1
            except DuplicateItemError:
                skipped.append(row["name"])
    return imported, skipped
