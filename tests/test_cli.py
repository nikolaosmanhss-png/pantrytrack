from pantrytrack.cli import main


def run(db, *args):
    return main(["--db", str(db), *args])


def test_full_workflow(tmp_path, capsys):
    db = tmp_path / "shop.db"
    assert run(db, "init") == 0
    assert run(db, "add", "Milk", "--unit", "l", "--qty", "6", "--reorder-level", "4",
               "--cost", "1.1", "--supplier", "Dairy Co") == 0
    assert run(db, "use", "Milk", "3") == 0
    assert "re-order level" in capsys.readouterr().out

    assert run(db, "reorder", "--out", str(tmp_path / "order.csv")) == 0
    out = capsys.readouterr().out
    assert "Dairy Co" in out and "Saved order list" in out
    assert (tmp_path / "order.csv").read_text(encoding="utf-8").startswith("supplier,item")

    assert run(db, "waste", "Milk", "1", "--reason", "expired") == 0
    assert run(db, "report", "--chart", str(tmp_path / "w.png"), "--out", str(tmp_path / "s.csv")) == 0
    assert (tmp_path / "w.png").exists() and (tmp_path / "s.csv").exists()

    assert run(db, "list") == 0
    assert "LOW" in capsys.readouterr().out


def test_errors_return_exit_code_1(tmp_path, capsys):
    db = tmp_path / "shop.db"
    run(db, "add", "Eggs", "--unit", "pcs", "--qty", "2")
    assert run(db, "use", "Eggs", "5") == 1
    assert "only 2 pcs in stock" in capsys.readouterr().err
    assert run(db, "receive", "Unknown", "1") == 1


def test_import_sample_file(tmp_path, capsys):
    from pathlib import Path

    sample = Path(__file__).parent.parent / "examples" / "sample_items.csv"
    assert run(tmp_path / "s.db", "import", str(sample)) == 0
    assert "Imported" in capsys.readouterr().out
