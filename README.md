# tanimachi

An opinionated Wappalyzer compatible fingerprint engine works along with HAR.

## Installation

```bash
pip install tanimachi
```

## Usage

```py
from tanimachi import (
    Wappalyzer,
    load_categories,
    load_fingerprints,
    load_groups,
    load_har,
)

fingerprints = load_fingerprints("/path/to/technologies/*.json")
# optional
categories = load_categories("/path/to/categories.json")
# optional
groups = load_groups("/path/to/groups.json")

har = load_har("/path/to/har")

wappalyzer = Wappalyzer(fingerprints, categories, groups)
detections = wappalyzer.analyze(har)

for detection in detections:
    print(detection)
```

## Known Limitation

- HAR file should only have one page. Multi-page HAR is not supported.
- The following fields are not supported:
  - `dns`
  - `probe`
  - `robots`
  - `xhr`
