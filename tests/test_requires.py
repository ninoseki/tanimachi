import pytest

from tanimachi import Wappalyzer, schemas


@pytest.fixture
def har():
    with open("tests/fixtures/har/quasar.dev.har") as f:
        return schemas.Har.model_validate_json(f.read())


@pytest.fixture
def fingerprints():
    with open("tests/fixtures/fingerprints/quasar.json") as f:
        return schemas.Fingerprints.model_validate_json(f.read())


def test_requires(har: schemas.Har, fingerprints: schemas.Fingerprints):
    wappalyzer = Wappalyzer(fingerprints=fingerprints)
    detections = wappalyzer.analyze(har)
    assert not any(detection.fingerprint.id == "Quasar" for detection in detections)
