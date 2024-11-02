from typing import Any

import pytest

from tanimachi import Wappalyzer, schemas


@pytest.fixture
def data():
    return {
        "should_be_matched": {
            "cookies": {
                "foo": "bar",
            },
            "website": "https://example.com",
        },
        "should_not_be_matched": {
            "cookies": {
                "404": "",
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
        detection.fingerprint.id == "should_be_matched" for detection in detections
    )
    assert not any(
        detection.fingerprint.id == "should_not_be_matched" for detection in detections
    )
