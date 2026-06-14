import pytest
from app.scraper import _parse_number


def test_parse_number_plain():
    assert _parse_number("1234") == 1234


def test_parse_number_with_commas():
    assert _parse_number("1,234") == 1234


def test_parse_number_k_suffix():
    assert _parse_number("1.2k") == 1200


def test_parse_number_k_whole():
    assert _parse_number("3k") == 3000


def test_parse_number_empty():
    assert _parse_number("") == 0


def test_parse_number_non_numeric():
    assert _parse_number("stars") == 0


def test_parse_number_with_spaces():
    assert _parse_number("  500  ") == 500
