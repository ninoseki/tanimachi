import itertools
import re
from collections.abc import Mapping
from typing import Annotated, Any

from loguru import logger
from pydantic import BaseModel, BeforeValidator, Field, RootModel, model_validator

from .api_model import APIModel
from .mixins import FileMixin, PatternMixin


class Pattern(BaseModel):
    string: str
    regex: re.Pattern = re.compile("", 0)
    version: str | None = None
    confidence: int = 100


def prepare_pattern(v: str | list[str], *, set_regex: bool = True) -> list[Pattern]:
    """Prepare a pattern for given string(s)

    Args:
        v (str | list[str]): string(s)
        set_regex (bool, optional): Set False only for DOM. DOM selector is not a regex so. Defaults to True.

    Returns:
        list[Pattern]: Patterns
    """
    pattern_objects: list[Pattern] = []

    if isinstance(v, list):
        for p in v:
            pattern_objects.extend(prepare_pattern(p, set_regex=set_regex))

        return pattern_objects

    attrs: dict[str, Any] = {}
    patterns = v.split("\\;")
    for index, expression in enumerate(patterns):
        if index == 0:
            attrs["string"] = expression
            if set_regex:
                try:
                    attrs["regex"] = re.compile(expression, re.I)  # type: ignore
                except re.error as e:
                    # Wappalyzer is a JavaScript application therefore some of the regex wont compile in Python.
                    logger.debug(f"Caught '{e}' compiling regex: {patterns}")
                    # regex that never matches:
                    # http://stackoverflow.com/a/1845097/413622
                    attrs["regex"] = re.compile(r"(?!x)x")  # type: ignore
        else:
            attr = expression.split(":")
            if len(attr) > 1:
                key = attr.pop(0)
                # This adds pattern['version'] when specified with "\\;version:\\1"
                attrs[str(key)] = ":".join(attr)

    pattern_objects.append(Pattern(**attrs))

    return pattern_objects


Patterns = Annotated[list[Pattern], BeforeValidator(prepare_pattern)]


def prepare_pattern_dict(v: dict[str, str | list[str]]) -> Mapping[str, list[Pattern]]:
    memo: dict[str, list[Pattern]] = {}
    for k in v:
        memo[k] = prepare_pattern(v[k])

    return memo


def prepare_headers(v: dict[str, str | list[str]]) -> Mapping[str, list[Pattern]]:
    return prepare_pattern_dict({k.lower(): _v for k, _v in v.items()})


Headers = Annotated[Mapping[str, list[Pattern]], BeforeValidator(prepare_headers)]
Cookies = Headers


def prepare_meta(v: str | list[str] | dict[str, str | list[str]]):
    thing = {"generator": v} if not isinstance(v, dict) else v

    return prepare_pattern_dict({k.lower(): v for k, v in thing.items()})


Meta = Annotated[Mapping[str, list[Pattern]], BeforeValidator(prepare_meta)]


class DomSelector(BaseModel):
    selector: str
    exists: bool | None = None
    text: list[Pattern] | None = None
    attributes: Mapping[str, list[Pattern]] | None = None


def prepare_string_dom(selector: str) -> list[DomSelector]:
    patterns = prepare_pattern(selector, set_regex=False)
    return [
        DomSelector(
            selector=pattern.string,
            exists=True,
            attributes={selector: [pattern]},
        )
        for pattern in patterns
    ]


def prepare_dom(
    thing: str | list[str] | dict[str, dict[str, str | list[str]]],
) -> list[DomSelector]:
    if isinstance(thing, str):
        return prepare_string_dom(thing)

    if isinstance(thing, list):
        return list(
            itertools.chain.from_iterable(prepare_string_dom(_o) for _o in thing)
        )

    selectors: list[DomSelector] = []
    if isinstance(thing, dict):
        for cssselect, clause in thing.items():
            # prepare regexes
            _prep_text_patterns = None
            _prep_attr_patterns = None
            _exists = None
            if clause.get("exists") is not None:
                _exists = True
            if clause.get("text"):
                _prep_text_patterns = prepare_pattern(clause["text"])
            if clause.get("attributes"):
                _prep_attr_patterns = {}
                for _key, pattern in clause["attributes"].items():  # type: ignore
                    _prep_attr_patterns[_key] = prepare_pattern(pattern)
            selectors.append(
                DomSelector(
                    selector=cssselect,
                    exists=_exists,
                    text=_prep_text_patterns,
                    attributes=_prep_attr_patterns,
                )
            )

    return selectors


Dom = Annotated[list[DomSelector], BeforeValidator(prepare_dom)]


def strings(v: str | list[str]) -> list[str]:
    if isinstance(v, list):
        return v

    return [v]


Strings = Annotated[list[str], BeforeValidator(strings)]


def numbers(v: int | list[int]) -> list[int]:
    if isinstance(v, list):
        return v

    return [v]


Numbers = Annotated[list[int], BeforeValidator(numbers)]


class Group(BaseModel):
    id: str = "N/A"
    name: str


class Groups(FileMixin, PatternMixin, RootModel):
    root: dict[str, Group]

    @model_validator(mode="after")
    def set_id(self):
        for k, v in self.root.items():
            v.id = k

        return self


class Category(BaseModel):
    id: str = "N/A"
    name: str
    groups: list[int] = Field(default_factory=list)
    priority: int = 0


class Categories(FileMixin, PatternMixin, RootModel):
    root: dict[str, Category]

    @model_validator(mode="after")
    def set_id(self):
        for k, v in self.root.items():
            v.id = k

        return self


class Fingerprint(APIModel):
    id: str = "N/A"

    website: str
    cats: list[int] = Field(default_factory=list)
    description: str | None = None
    icon: str | None = None
    cpe: str | None = None
    saas: bool | None = None
    oss: bool | None = None
    pricing: Strings = Field(default_factory=list)

    implies: Strings = Field(default_factory=list)
    requires: Strings = Field(default_factory=list)
    requires_category: Numbers = Field(default_factory=list)
    excludes: Strings = Field(default_factory=list)

    dom: Dom = Field(default_factory=list)

    headers: Headers = Field(default_factory=dict)
    cookies: Cookies = Field(default_factory=dict)
    meta: Meta = Field(default_factory=dict)

    html: Patterns = Field(default_factory=list)
    text: Patterns = Field(default_factory=list)
    url: Patterns = Field(default_factory=list)
    script_src: Patterns = Field(default_factory=list)
    scripts: Patterns = Field(default_factory=list)
    css: Patterns = Field(default_factory=list)


class Fingerprints(PatternMixin, FileMixin, RootModel):
    root: dict[str, Fingerprint]

    @model_validator(mode="after")
    def set_id(self):
        for k, v in self.root.items():
            v.id = k

        return self
