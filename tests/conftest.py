from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import socket

import pytest

from equity_research.data import load_dataset
from equity_research.models import Candidate, Config
import json

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("network access is forbidden in research tests")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)


@pytest.fixture
def dataset():
    return load_dataset(FIXTURES / "synthetic_daily.csv", FIXTURES / "data_manifest.json")


@pytest.fixture
def candidate():
    return Candidate.from_dict(json.loads((FIXTURES / "candidate.json").read_text()))


@pytest.fixture
def config():
    return Config.from_dict({})


@pytest.fixture
def future():
    def change(dataset, prices):
        bars = list(dataset.bars[:60])
        for original, row in zip(dataset.bars[60:], prices):
            bars.append(replace(original, **dict(zip(("open", "high", "low", "close"), map(Decimal, map(str, row))))))
        return replace(dataset, bars=tuple(bars))
    return change
