import json

import pytest

from sublylocal.translate import _parse_response


def test_parse_response_restores_order() -> None:
    content = json.dumps([{"id": 1, "text": "Deux"}, {"id": 0, "text": "Un"}])
    assert _parse_response(content, 2) == ["Un", "Deux"]


def test_parse_response_rejects_missing_item() -> None:
    with pytest.raises(ValueError):
        _parse_response('[{"id": 0, "text": "Un"}]', 2)
