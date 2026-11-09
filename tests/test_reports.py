import pytest

from pantrytrack import inventory as inv
from pantrytrack import reports


@pytest.fixture
def stocked(conn):
    inv.add_item(conn, "Tomatoes", "kg", quantity=20, unit_cost=1.5)
    inv.add_item(conn, "Feta", "kg", quantity=10, unit_cost=8.0)
    inv.use(conn, "Tomatoes", 12)
    inv.waste(conn, "Tomatoes", 3, reason="Spoiled")
    inv.use(conn, "Feta", 4)
    inv.waste(conn, "Feta", 1, reason="expired")
    return conn


def test_movements_df(stocked):
    df = reports.movements_df(stocked)
    assert len(df) == 6
    assert set(df["kind"]) == {"in", "use", "waste"}


def test_summary_waste_cost_and_rate(stocked):
    df = reports.summary(stocked).set_index("item")
    assert df.loc["Tomatoes", "wasted"] == 3
    assert df.loc["Tomatoes", "waste_cost"] == 4.5
    assert df.loc["Tomatoes", "waste_rate_pct"] == 20.0  # 3 / (12 + 3)
    assert df.loc["Feta", "waste_cost"] == 8.0
    # sorted by waste cost, highest first
    assert list(df.index) == ["Feta", "Tomatoes"]


def test_summary_empty_database(conn):
    assert reports.summary(conn).empty


def test_waste_by_reason_normalises_case(stocked):
    df = reports.waste_by_reason(stocked)
    assert set(df["reason"]) == {"spoiled", "expired"}


def test_invalid_days(conn):
    with pytest.raises(ValueError):
        reports.summary(conn, days=0)


def test_plot_waste_creates_png(stocked, tmp_path):
    out = reports.plot_waste(stocked, tmp_path / "waste.png")
    assert out.exists() and out.stat().st_size > 1000


def test_plot_waste_with_no_data(conn, tmp_path):
    out = reports.plot_waste(conn, tmp_path / "empty.png")
    assert out.exists()
