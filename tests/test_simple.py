import pytest_stepfunctions


def test_add() -> None:
    assert 7 == pytest_stepfunctions.add(3, 4)
    assert 4 == pytest_stepfunctions.add(3, 1)
    assert 10 == pytest_stepfunctions.add(-31, 41)
