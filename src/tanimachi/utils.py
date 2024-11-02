from pathlib import Path

from . import schemas


def load_har(path: str | Path) -> schemas.Har:
    """Load HAR file.

    Args:
        path (str | Path): Path to the HAR file.

    Returns:
        schemas.Har: HAR.
    """
    return schemas.Har.model_validate_file(path)


def load_fingerprints(pattern: str) -> schemas.Fingerprints:
    """Load fingerprints.

    Args:
        dir (str): Glob patterns for the fingerprint files.

    Returns:
        schemas.Fingerprint: Fingerprints.
    """
    return schemas.Fingerprints.model_validate_pattern(pattern)


def load_categories(path: str | Path) -> schemas.Categories:
    """Load categories.

    Args:
        path (str | Path): Path to the categories file.

    Returns:
        schemas.Categories: Categories
    """
    return schemas.Categories.model_validate_file(path)


def load_groups(path: str | Path) -> schemas.Groups:
    """Load groups.

    Args:
        path (str | Path): Path to the groups file.

    Returns:
        schemas.Groups: Groups
    """
    path = Path(path) if isinstance(path, str) else path
    return schemas.Groups.model_validate_file(path)
