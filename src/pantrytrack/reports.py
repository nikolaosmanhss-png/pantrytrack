"""Reporting with pandas and matplotlib: usage, waste and cost summaries."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

MOVEMENT_COLUMNS = ["date", "item", "category", "unit", "kind", "quantity", "unit_cost", "cost", "note"]


def _cutoff(days: int | None) -> str | None:
    if days is None:
        return None
    if days <= 0:
        raise ValueError("days must be greater than zero")
    start = datetime.now(timezone.utc) - timedelta(days=days)
    return start.isoformat(timespec="seconds")


def movements_df(conn: sqlite3.Connection, days: int | None = None, item: str | None = None) -> pd.DataFrame:
    """Return all stock movements as a DataFrame (newest first)."""
    query = """
        SELECT m.created_at AS date, i.name AS item, i.category, i.unit, m.kind,
               m.quantity, m.unit_cost, ROUND(m.quantity * m.unit_cost, 2) AS cost, m.note
        FROM movements m JOIN items i ON i.id = m.item_id
        WHERE 1 = 1
    """
    params: list = []
    cutoff = _cutoff(days)
    if cutoff:
        query += " AND m.created_at >= ?"
        params.append(cutoff)
    if item:
        query += " AND i.name = ? COLLATE NOCASE"
        params.append(item)
    query += " ORDER BY m.created_at DESC, m.id DESC"
    df = pd.read_sql_query(query, conn, params=params)
    return df if not df.empty else pd.DataFrame(columns=MOVEMENT_COLUMNS)


def summary(conn: sqlite3.Connection, days: int | None = 30) -> pd.DataFrame:
    """Per-item totals of received, used and wasted stock plus waste cost and waste rate.

    ``waste_rate`` = wasted / (used + wasted). A high value points to over-ordering,
    poor rotation (FIFO) or storage problems.
    """
    df = movements_df(conn, days=days)
    cols = ["item", "unit", "received", "used", "wasted", "waste_cost", "waste_rate_pct"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    pivot = df.pivot_table(
        index=["item", "unit"], columns="kind", values="quantity", aggfunc="sum", fill_value=0
    )
    for kind in ("in", "use", "waste"):
        if kind not in pivot.columns:
            pivot[kind] = 0.0
    waste_cost = df[df["kind"] == "waste"].groupby(["item", "unit"])["cost"].sum()
    out = pd.DataFrame(
        {
            "received": pivot["in"],
            "used": pivot["use"],
            "wasted": pivot["waste"],
        }
    )
    out["waste_cost"] = waste_cost.reindex(out.index).fillna(0).round(2)
    consumed = out["used"] + out["wasted"]
    out["waste_rate_pct"] = (out["wasted"] / consumed.where(consumed > 0) * 100).fillna(0).round(1)
    out = out.reset_index().sort_values(["waste_cost", "item"], ascending=[False, True])
    return out[cols].reset_index(drop=True)


def waste_by_reason(conn: sqlite3.Connection, days: int | None = 30) -> pd.DataFrame:
    df = movements_df(conn, days=days)
    df = df[df["kind"] == "waste"]
    if df.empty:
        return pd.DataFrame(columns=["reason", "events", "cost"])
    df = df.assign(reason=df["note"].fillna("(not given)").str.lower())
    out = df.groupby("reason").agg(events=("item", "count"), cost=("cost", "sum")).reset_index()
    out["cost"] = out["cost"].round(2)
    return out.sort_values("cost", ascending=False).reset_index(drop=True)


def plot_waste(conn: sqlite3.Connection, out_path: str | Path, days: int | None = 30, top: int = 10) -> Path:
    """Save a horizontal bar chart of the items with the highest waste cost."""
    import matplotlib

    matplotlib.use("Agg")  # no display needed (works on servers and in CI)
    import matplotlib.pyplot as plt

    data = summary(conn, days=days)
    data = data[data["waste_cost"] > 0].head(top).iloc[::-1]
    out_path = Path(out_path)
    fig, ax = plt.subplots(figsize=(8, max(2.5, 0.45 * len(data) + 1.2)))
    if data.empty:
        ax.text(0.5, 0.5, "No waste recorded in this period", ha="center", va="center")
        ax.set_axis_off()
    else:
        ax.barh(data["item"], data["waste_cost"], color="#c0504d")
        for y, v in enumerate(data["waste_cost"]):
            ax.text(v, y, f" €{v:,.2f}", va="center", fontsize=9)
        ax.set_xlabel("Waste cost (€)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.margins(x=0.15)
    period = f"last {days} days" if days else "all time"
    ax.set_title(f"Top items by waste cost ({period})")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
