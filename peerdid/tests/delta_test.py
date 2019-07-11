import json
import re

from ..delta import Delta


SAMPLE_CHANGE = '{"deleted": ["key-1"]}'
SAMPLE_CHANGE_BASE64 = "eyJkZWxldGVkIjogWyJrZXktMSJdfQ=="


def test_ctor_with_json_str(sample_delta):
    d = sample_delta
    assert d.change == SAMPLE_CHANGE_BASE64
    assert d.by == []
    assert d.when
    assert d.hash


def test_ctor_with_json_bytes():
    d = Delta(SAMPLE_CHANGE.encode('utf-8'), [])
    assert d.change == SAMPLE_CHANGE_BASE64


def test_ctor_with_base64_str():
    d = Delta(SAMPLE_CHANGE_BASE64, [])
    assert d.change == SAMPLE_CHANGE_BASE64


def test_ctor_with_base64_bytes():
    d = Delta(SAMPLE_CHANGE_BASE64.encode('ascii'), [])
    assert d.change == SAMPLE_CHANGE_BASE64


def test_ctor_with_dict(sample_delta):
    x = sample_delta.change_json_dict
    assert x["deleted"][0] == "key-1"


def test_change_str(sample_delta):
    assert sample_delta.change_json_str == SAMPLE_CHANGE


def test_change_dict(sample_delta):
    x = sample_delta.change_json_dict
    assert x["deleted"][0] == "key-1"


def test_str(sample_delta):
    s = str(sample_delta)
    assert '"change": "%s"' % SAMPLE_CHANGE_BASE64 in s
    assert '"by": []' in s
    assert re.search(r'"when": "20[^"]+"', s)


def test_round_trip(sample_delta):
    d2 = Delta.from_json(sample_delta.to_json())
    assert sample_delta.hash == d2.hash
    assert sample_delta.when == d2.when
    assert sample_delta.change == d2.change
    assert sample_delta.by == d2.by


def test_comparison(sample_delta):
    d2 = Delta(SAMPLE_CHANGE_BASE64, [], sample_delta.when)
    assert sample_delta == sample_delta
    assert sample_delta == d2
    d3 = Delta('{}', [])
    assert d2 != d3


def test_hashable(sample_delta):
    x = [sample_delta, Delta(SAMPLE_CHANGE, [])]
    y = set(x)
    assert len(y) == 1