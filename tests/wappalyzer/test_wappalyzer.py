import pytest

from tanimachi import schemas
from tanimachi.wappalyzer import Wappalyzer


@pytest.fixture
def fingerprints():
    with open("tests/fixtures/wappalyzer/a.json") as f:
        return schemas.Fingerprints.model_validate_json(f.read())


def test_analyze(har: schemas.Har, fingerprints: schemas.Fingerprints):
    wappalyzer = Wappalyzer(fingerprints=fingerprints)
    assert len(wappalyzer.analyze(har)) > 0
