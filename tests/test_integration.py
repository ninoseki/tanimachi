import glob
import json
import tempfile
from typing import Any

import pytest
from git import Repo

from tanimachi import Wappalyzer, schemas
from tanimachi.wappalyzer import (
    analyze_css,
    analyze_headers,
    analyze_html,
    analyze_meta,
    analyze_scripts,
    analyze_url,
)


@pytest.fixture
def repo():
    with tempfile.TemporaryDirectory() as dir:
        Repo.clone_from("https://github.com/tunetheweb/wappalyzer/", dir)
        yield dir


@pytest.fixture
def fingerprints(repo: str):
    memo: dict[str, Any] = {}
    for path in glob.glob(f"{repo}/src/technologies/*.json"):
        with open(path) as f:
            memo.update(json.load(f))

    return schemas.Fingerprints.model_validate(memo)


@pytest.fixture
def har():
    with open("tests/fixtures/har/example.com.har") as f:
        return schemas.Har.model_validate_json(f.read())


def test_integration(har: schemas.Har, fingerprints: schemas.Fingerprints):
    wappalyzer = Wappalyzer(fingerprints=fingerprints)
    # analyze_dom is very slow so skip it
    assert (
        len(
            wappalyzer.analyze(
                har,
                analyzes=[
                    analyze_css,
                    analyze_headers,
                    analyze_html,
                    analyze_meta,
                    analyze_scripts,
                    analyze_url,
                ],
            )
        )
        > 0
    )
