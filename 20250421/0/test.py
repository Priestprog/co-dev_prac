import pytest
from sqroot import sqroots

def test_two_roots():
    assert sqroots("1 -3 2") == "1.0 2.0"

def test_one_root():
    assert sqroots("1 2 1") == "-1.0"

def test_no_roots():
    assert sqroots("1 0 1") == ""

def test_invalid_input_raises():
    with pytest.raises(ValueError):
        sqroots("0 2 1")
