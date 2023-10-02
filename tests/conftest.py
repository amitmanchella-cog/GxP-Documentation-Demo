import sqlite3

import pytest
from fastapi.testclient import TestClient

from sst import main as app_module
from sst.regimes import load_regime
from sst.seed import seed


@pytest.fixture()
def conn():
    c = sqlite3.connect(":memory:", check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    seed(c)
    return c


@pytest.fixture()
def client(conn):
    app_module.reset_state(conn=conn, regime=load_regime("gmp"))
    with TestClient(app_module.app) as tc:
        yield tc
    app_module.reset_state()
