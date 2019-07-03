import re

from ..delta import Delta

def test_ctor():
    d = Delta("abc", [])
    assert d.change == "abc"
    assert d.by == []
    assert d.when
    assert d.id

def test_str():
    d = Delta("abc", [])
    s = str(d)
    print(s)
    m = re.match(r'{"change": "abc", "by": \[\], "when": "20[^"]+", "id": "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"}', s)
    assert bool(m)

def test_round_trip():
    d1 = Delta("abc", [])
    d2 = Delta.from_json(d1.to_json())
    assert d1.id == d2.id
    assert d1.when == d2.when
    assert d1.change == d2.change
    assert d1.by == d2.by