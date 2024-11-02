import tempfile
from collections.abc import Iterable
from functools import lru_cache

import pytest
from _pytest.fixtures import SubRequest
from git import Repo

from tanimachi import Wappalyzer, schemas


@lru_cache(maxsize=1)
def get_fingerprints() -> Iterable[schemas.Fingerprint]:
    with tempfile.TemporaryDirectory() as dir:
        Repo.clone_from("https://github.com/enthec/webappanalyzer", dir)
        fingerprints = schemas.Fingerprints.model_validate_pattern(
            f"{dir}/src/technologies/*.json"
        )
        return fingerprints.root.values()


@pytest.fixture(params=get_fingerprints())
def fingerprint(request: SubRequest):
    return request.param


def test_integration(har: schemas.Har, fingerprint: schemas.Fingerprint):
    fingerprints = schemas.Fingerprints(root={fingerprint.id: fingerprint})
    wappalyzer = Wappalyzer(fingerprints=fingerprints)
    assert len(wappalyzer.analyze(har)) >= 0
