import pytest

from pantrytrack.db import connect


@pytest.fixture
def conn():
    """A fresh in-memory database for every test."""
    c = connect(":memory:")
    yield c
    c.close()
