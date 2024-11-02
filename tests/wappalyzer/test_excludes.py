from typing import Any

import pytest

from tanimachi import Wappalyzer, schemas


@pytest.fixture
def data():
    return {
        "should_be_excluded": {
            "dom": {"title": {"text": "Example Domain"}},
            "website": "https://example.com",
        },
        "should_be_included": {
            "dom": {"title": {"text": "Example Domain"}},
            "website": "https://example.com",
        },
        "match_all": {
            "excludes": ["should_be_excluded"],
            "dom": {
                "*": {"exists": ""},
            },
            "website": "https://example.com",
        },
    }


@pytest.fixture
def fingerprints(data: Any):
    return schemas.Fingerprints.model_validate(data)


def test_requires(har: schemas.Har, fingerprints: schemas.Fingerprints):
    wappalyzer = Wappalyzer(fingerprints=fingerprints)
    detections = wappalyzer.analyze(har)
    assert any(
        detection.fingerprint.id == "should_be_included" for detection in detections
    )
    assert not any(
        detection.fingerprint.id == "should_be_excluded" for detection in detections
    )
