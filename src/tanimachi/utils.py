import glob
import json
from pathlib import Path
from typing import Any

from . import schemas


def load_har(path: str | Path) -> schemas.Har:
    """Load HAR file.

    Args:
        path (str | Path): Path to the HAR file.

    Returns:
        schemas.Har: HAR.
    """
    path = Path(path) if isinstance(path, str) else path
    return schemas.Har.model_validate_json(path.read_text())


def load_fingerprints(pattern: str) -> schemas.Fingerprints:
    """Load fingerprints.

    Args:
        dir (str): Glob patterns for the fingerprint files.

    Returns:
        schemas.Fingerprint: Fingerprints.
    """
    memo: dict[str, Any] = {}
    for path in glob.glob(pattern):
        memo.update(json.loads(Path(path).read_text()))

    return schemas.Fingerprints.model_validate(memo)


def load_categories(path: str | Path) -> schemas.Categories:
    """Load categories.

    Args:
        path (str | Path): Path to the categories file.

    Returns:
        schemas.Categories: Categories
    """
    path = Path(path) if isinstance(path, str) else path
    return schemas.Categories.model_validate_json(path.read_text())


def load_groups(path: str | Path) -> schemas.Groups:
    """Load groups.

    Args:
        path (str | Path): Path to the groups file.

    Returns:
        schemas.Groups: Groups
    """
    path = Path(path) if isinstance(path, str) else path
    return schemas.Groups.model_validate_json(path.read_text())
