import glob
import json
import tempfile
from functools import lru_cache
from typing import Any

import pytest
from _pytest.fixtures import SubRequest
from git import Repo

from tanimachi import Wappalyzer, schemas


@lru_cache(maxsize=1)
def get_fingerprints():
    with tempfile.TemporaryDirectory() as dir:
        Repo.clone_from("https://github.com/enthec/webappanalyzer", dir)

        memo: dict[str, Any] = {}
        for path in glob.glob(f"{dir}/src/technologies/*.json"):
            with open(path) as f:
                memo.update(json.load(f))

        return schemas.Fingerprints.model_validate(memo).root.values()


@pytest.fixture(params=get_fingerprints())
def fingerprint(request: SubRequest):
    return request.param


def test_integration(har: schemas.Har, fingerprint: schemas.Fingerprint):
    fingerprints = schemas.Fingerprints(root={fingerprint.id: fingerprint})
    wappalyzer = Wappalyzer(fingerprints=fingerprints)
    assert len(wappalyzer.analyze(har)) >= 0
