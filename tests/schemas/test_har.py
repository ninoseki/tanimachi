import json
from typing import Any

import pytest

from tanimachi.schemas import Har


@pytest.fixture
def example():
    with open("tests/fixtures/har/example.com.har") as f:
        return json.load(f)


def test_har(example: Any):
    assert Har.model_validate(example)
