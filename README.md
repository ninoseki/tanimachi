# tanimachi

An opinionated Wappalyzer compatible fingerprint engine works along with [HAR](<https://en.wikipedia.org/wiki/HAR_(file_format)>).

> [!NOTE]
> This repository does not contain fingerprints themselves.
> You need to get them from Wappalyzer compatible repositories such as:
>
> - [enthec/webappanalyzer](https://github.com/enthec/webappanalyzer)
> - [tunetheweb/wappalyzer](https://github.com/tunetheweb/wappalyzer)

## Installation

```bash
pip install tanimachi
```

## Usage

```py
from tanimachi import (
    Categories,
    Fingerprints,
    Groups,
    Har,
    Wappalyzer,
)

fingerprints = Fingerprints.model_validate_pattern("/path/to/technologies/*.json")
categories = Categories.model_validate_file("/path/to/categories.json")
groups = Groups.model_validate_file("/path/to/groups.json")
har = Har.model_validate_file("./tests/fixtures/har/example.har")

wappalyzer = Wappalyzer(fingerprints, categories=categories, groups=groups)
detections = wappalyzer.analyze(har)
```

## Known Limitations

- HAR file should only have one page. Multi-page HAR is not supported.
- The following fields are not supported:
  - `dns`
  - `probe`
  - `robots`
  - `xhr`

## Credits

Wappalyzer detection logic (functions, etc.) are forked from [chorsley/python-Wappalyzer](https://github.com/chorsley/python-Wappalyzer).
