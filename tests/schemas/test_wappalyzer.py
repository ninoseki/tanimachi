import json
from typing import Any

import pytest

from tanimachi.schemas import Fingerprints


@pytest.fixture
def fingerprints():
    with open("tests/fixtures/wappalyzer/a.json") as f:
        return json.loads(f.read())


def test_fingerprints(fingerprints: Any):
    assert Fingerprints.model_validate(fingerprints)
