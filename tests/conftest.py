import pytest

from tanimachi import schemas


@pytest.fixture
def har():
    with open("tests/fixtures/har/example.har") as f:
        return schemas.Har.model_validate_json(f.read())
