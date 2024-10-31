import pytest

from tanimachi import schemas
from tanimachi.wappalyzer import HarWrapper, Wappalyzer, analyze_dom


@pytest.fixture
def har():
    with open("tests/fixtures/har/example.com.har") as f:
        return schemas.Har.model_validate_json(f.read())


@pytest.fixture
def fingerprints():
    with open("tests/fixtures/wappalyzer/a.json") as f:
        return schemas.Fingerprints.model_validate_json(f.read())


def test_analyze(har: schemas.Har, fingerprints: schemas.Fingerprints):
    wappalyzer = Wappalyzer(fingerprints=fingerprints)
    assert len(wappalyzer.analyze(har)) > 0


@pytest.mark.parametrize(
    ("fingerprint", "expected"),
    [
        (schemas.Fingerprint(dom={"h1": {"exists": ""}}, website="dummy"), 1),  # type: ignore
        (schemas.Fingerprint(dom={"h2": {"exists": ""}}, website="dummy"), 0),  # type: ignore
        (
            schemas.Fingerprint(
                dom={"h1": {"text": "Example Domain"}},  # type: ignore
                website="dummy",
            ),
            1,
        ),
        (schemas.Fingerprint(dom={"h1": {"text": "foo"}}, website="dummy"), 0),  # type: ignore
        (
            schemas.Fingerprint(
                dom={
                    "link[id='elpt-portfolio-css-css'][href*='portfolio-elementor']": {
                        "attributes": {"href": "ver=([\\d\\.]+)\\;version:\\1"}
                    },
                    "style#powerfolio-portfolio-block-style-inline-css": {"exists": ""},
                },  # type: ignore
                website="dummy",
            ),
            0,
        ),
        (
            schemas.Fingerprint(
                dom="h1\\;confidence:40",  # type: ignore
                website="dummy",
            ),
            1,
        ),
        (
            schemas.Fingerprint(
                dom="form[name='formLogin'][action='login.aspx' i][id='formLogin']\\;confidence:40",  # type: ignore
                website="dummy",
            ),
            0,
        ),
        (
            schemas.Fingerprint(
                dom=["h1\\;confidence:40"],  # type: ignore
                website="dummy",
            ),
            1,
        ),
        (
            schemas.Fingerprint(
                dom=[
                    "form[name='formLogin'][action='login.aspx' i][id='formLogin']\\;confidence:40"  # type: ignore
                ],
                website="dummy",
            ),
            0,
        ),
    ],
)
def test_analyze_dom(har: schemas.Har, fingerprint: schemas.Fingerprint, expected: int):
    wrapper = HarWrapper(log=har.log)
    assert len(analyze_dom(wrapper, fingerprint=fingerprint)) == expected
