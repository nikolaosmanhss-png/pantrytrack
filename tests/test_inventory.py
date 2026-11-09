import pytest

from pantrytrack import inventory as inv


def test_add_and_get_item(conn):
    item = inv.add_item(conn, "Feta", "kg", category="dairy", quantity=5, reorder_level=2, unit_cost=8.5)
    assert item.quantity == 5
    assert inv.get_item(conn, "feta").name == "Feta"  # case-insensitive lookup
    assert item.stock_value == 42.5


def test_duplicate_item_is_rejected(conn):
    inv.add_item(conn, "Feta", "kg")
    with pytest.raises(inv.DuplicateItemError):
        inv.add_item(conn, "FETA", "kg")


@pytest.mark.parametrize("field", ["quantity", "reorder_level", "unit_cost"])
def test_negative_values_are_rejected(conn, field):
    with pytest.raises(ValueError):
        inv.add_item(conn, "Milk", "l", **{field: -1})


def test_receive_use_and_waste_update_stock(conn):
    inv.add_item(conn, "Tomatoes", "kg", quantity=10, unit_cost=1.2)
    inv.receive(conn, "Tomatoes", 5, unit_cost=1.5)
    inv.use(conn, "Tomatoes", 6)
    item = inv.waste(conn, "Tomatoes", 1, reason="spoiled")
    assert item.quantity == pytest.approx(8)
    assert item.unit_cost == 1.5


def test_cannot_take_more_than_in_stock(conn):
    inv.add_item(conn, "Eggs", "pcs", quantity=12)
    with pytest.raises(inv.InsufficientStockError):
        inv.use(conn, "Eggs", 13)
    assert inv.get_item(conn, "Eggs").quantity == 12  # nothing changed


def test_float_rounding_does_not_block_last_portion(conn):
    # regression: 1 - 0.9 - 0.1 used to raise a CHECK constraint error
    inv.add_item(conn, "Cream", "l", quantity=1)
    inv.use(conn, "Cream", 0.9)
    assert inv.use(conn, "Cream", 0.1).quantity == 0


def test_unknown_item(conn):
    with pytest.raises(inv.ItemNotFoundError):
        inv.use(conn, "Caviar", 1)


def test_zero_quantity_is_rejected(conn):
    inv.add_item(conn, "Flour", "kg", quantity=10)
    with pytest.raises(ValueError):
        inv.receive(conn, "Flour", 0)


def test_stock_take_adjustment(conn):
    inv.add_item(conn, "Olive oil", "l", quantity=10)
    assert inv.adjust(conn, "Olive oil", 7.5).quantity == 7.5
    assert inv.adjust(conn, "Olive oil", 9).quantity == 9


def test_low_stock_and_reorder_list(conn):
    inv.add_item(conn, "Milk", "l", quantity=3, reorder_level=4, unit_cost=1.1, supplier="Dairy Co")
    inv.add_item(conn, "Flour", "kg", quantity=20, reorder_level=5, unit_cost=0.8, supplier="Mill SA")
    inv.add_item(conn, "Napkins", "box", quantity=0)  # no re-order level -> never "low"

    assert [i.name for i in inv.low_stock(conn)] == ["Milk"]

    order = inv.reorder_list(conn, multiplier=2)
    assert order == [
        {"supplier": "Dairy Co", "item": "Milk", "unit": "l", "in_stock": 3,
         "order_qty": 5, "est_cost": 5.5}
    ]


def test_remove_item_deletes_history(conn):
    inv.add_item(conn, "Basil", "bunch", quantity=3)
    inv.remove_item(conn, "Basil")
    assert inv.list_items(conn) == []
    assert conn.execute("SELECT COUNT(*) FROM movements").fetchone()[0] == 0


def test_import_csv(conn, tmp_path):
    csv_file = tmp_path / "items.csv"
    csv_file.write_text(
        "name,unit,category,quantity,reorder_level,unit_cost,supplier\n"
        "Rice,kg,dry goods,25,5,1.4,Mill SA\n"
        "Rice,kg,dry goods,1,1,1,Mill SA\n"
        "Lemons,pcs,produce,40,10,0.2,\n",
        encoding="utf-8",
    )
    imported, skipped = inv.import_items_csv(conn, csv_file)
    assert imported == 2
    assert skipped == ["Rice"]
    assert inv.get_item(conn, "Lemons").supplier is None


def test_import_csv_requires_columns(conn, tmp_path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("title,amount\nRice,3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="name, unit"):
        inv.import_items_csv(conn, csv_file)
