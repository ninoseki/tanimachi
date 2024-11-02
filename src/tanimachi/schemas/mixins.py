import glob
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class FileMixin(BaseModel):
    @classmethod
    def model_validate_file(cls, path: str | Path):
        """Validate the model from a file.

        Args:
            path (str | Path): Path
        """
        path = Path(path) if isinstance(path, str) else path
        return cls.model_validate_json(path.read_text())


class PatternMixin(BaseModel):
    @classmethod
    def model_validate_pattern(cls, pattern: str):
        """Validate the model from a glob pattern.

        Args:
            pattern (str): Glob pattern
        """
        memo: dict[str, Any] = {}
        for path in glob.glob(pattern):
            memo.update(json.loads(Path(path).read_text()))

        return cls.model_validate(memo)
