import itertools
from collections.abc import Callable
from functools import cached_property, partial
from typing import Any, cast

from pydantic import BaseModel
from returns.pipeline import pipe
from selectolax.parser import HTMLParser

from . import schemas


def is_javascript(entry: schemas.Entry) -> bool:
    return entry.request.method == "GET" and any(
        [
            entry.response.content.mime_type.startswith("application/javascript"),
            entry.response.content.mime_type.startswith("text/javascript"),
        ]
    )


def is_stylesheet(entry: schemas.Entry) -> bool:
    return (
        entry.request.method == "GET"
        and entry.response.content.mime_type.startswith("text/css")
    )


def is_html(entry: schemas.Entry) -> bool:
    return (
        entry.request.method == "GET"
        and entry.response.content.mime_type.startswith("text/html")
    )


class HarWrapper(schemas.Har):
    @cached_property
    def stylesheet_entries(self):
        return [entry for entry in self.log.entries if is_stylesheet(entry)]

    @cached_property
    def stylesheets(self) -> list[str]:
        stylesheets = [entry.response.content.text for entry in self.stylesheet_entries]
        return [stylesheet for stylesheet in stylesheets if stylesheet]

    @cached_property
    def javascript_entries(self):
        return [entry for entry in self.log.entries if is_javascript(entry)]

    @cached_property
    def scripts(self) -> list[str]:
        scripts = [entry.response.content.text for entry in self.javascript_entries]
        return [script for script in scripts if script]

    @cached_property
    def script_src(self):
        return [entry.request.url for entry in self.javascript_entries]

    @cached_property
    def html_entry(self):
        for entry in self.log.entries:
            if is_html(entry):
                return entry

        raise ValueError("No HTML entry found")

    @cached_property
    def url(self):
        return str(self.html_entry.request.url)

    @cached_property
    def html(self) -> str:
        if not self.html_entry.response.content.text:
            raise ValueError("No HTML content found")

        return self.html_entry.response.content.text

    @cached_property
    def headers(self):
        return {
            header.name: header.value for header in self.html_entry.response.headers
        }

    @cached_property
    def cookies(self):
        return {
            header.name: header.value for header in self.html_entry.response.cookies
        }

    @cached_property
    def dom(self):
        return HTMLParser(self.html)

    @cached_property
    def meta(self):
        memo: dict[str, str] = {}

        for meta in self.dom.css("meta"):
            name = meta.attributes.get("name")
            content = meta.attributes.get("content")
            if name and content:
                memo[name.lower()] = content

        return memo


class Detection(BaseModel):
    url: str
    fingerprint: schemas.Fingerprint
    app_type: str
    pattern: schemas.Pattern
    value: str
    key: str = ""
    categories: list[schemas.Category] | None = None
    groups: list[schemas.Group] | None = None


def analyze_url(har: HarWrapper, fingerprint: schemas.Fingerprint) -> list[Detection]:
    detections: list[Detection] = []

    for pattern in fingerprint.url:
        if pattern.regex.search(har.url):
            detections.append(
                Detection(
                    url=har.url,
                    fingerprint=fingerprint,
                    app_type="url",
                    pattern=pattern,
                    value=har.url,
                )
            )

    return detections


def analyze_headers(
    har: HarWrapper, fingerprint: schemas.Fingerprint
) -> list[Detection]:
    detections: list[Detection] = []

    for name, patterns in fingerprint.headers.items():
        if name not in har.headers:
            continue

        content = har.headers[name]
        for pattern in patterns:
            if pattern.regex.search(content):
                detections.append(
                    Detection(
                        url=har.url,
                        fingerprint=fingerprint,
                        app_type="headers",
                        pattern=pattern,
                        value=content,
                        key=name,
                    )
                )

    return detections


def analyze_cookies(
    har: HarWrapper, fingerprint: schemas.Fingerprint
) -> list[Detection]:
    detections: list[Detection] = []

    for name, patterns in fingerprint.cookies.items():
        if name not in har.cookies:
            continue

        content = har.cookies[name]
        for pattern in patterns:
            if pattern.regex.search(content):
                detections.append(
                    Detection(
                        url=har.url,
                        fingerprint=fingerprint,
                        app_type="cookies",
                        pattern=pattern,
                        value=content,
                        key=name,
                    )
                )

    return detections


def analyze_scripts(
    har: HarWrapper, fingerprint: schemas.Fingerprint
) -> list[Detection]:
    detections: list[Detection] = []

    for pattern in fingerprint.scripts:
        for script in har.scripts:
            if pattern.regex.search(script):
                detections.append(
                    Detection(
                        url=har.url,
                        fingerprint=fingerprint,
                        app_type="scripts",
                        pattern=pattern,
                        value=script,
                    )
                )

    return detections


def analyze_css(har: HarWrapper, fingerprint: schemas.Fingerprint) -> list[Detection]:
    detections: list[Detection] = []

    for pattern in fingerprint.css:
        for stylesheet in har.stylesheets:
            if pattern.regex.search(stylesheet):
                detections.append(
                    Detection(
                        url=har.url,
                        fingerprint=fingerprint,
                        app_type="css",
                        pattern=pattern,
                        value=stylesheet,
                    )
                )

    return detections


def analyze_meta(har: HarWrapper, fingerprint: schemas.Fingerprint) -> list[Detection]:
    detections: list[Detection] = []

    for name, patterns in fingerprint.meta.items():
        if name in har.meta:
            content = har.meta[name]
            for pattern in patterns:
                if pattern.regex.search(content):
                    detections.append(
                        Detection(
                            url=har.url,
                            fingerprint=fingerprint,
                            app_type="meta",
                            pattern=pattern,
                            value=content,
                            key=name,
                        )
                    )

    return detections


def analyze_html(har: HarWrapper, fingerprint: schemas.Fingerprint) -> list[Detection]:
    detections: list[Detection] = []

    for pattern in fingerprint.html:
        if pattern.regex.search(har.html):
            detections.append(
                Detection(
                    url=har.url,
                    fingerprint=fingerprint,
                    app_type="html",
                    pattern=pattern,
                    value=har.html,
                )
            )

    return detections


def analyze_dom(har: HarWrapper, fingerprint: schemas.Fingerprint) -> list[Detection]:  # noqa: C901
    detections: list[Detection] = []

    for selector in fingerprint.dom:
        for item in har.dom.css(selector.selector):
            if selector.exists:
                detections.append(
                    Detection(
                        url=har.url,
                        fingerprint=fingerprint,
                        app_type="dom",
                        pattern=schemas.Pattern(string=selector.selector),
                        value="",
                    )
                )

            if selector.text:
                for pattern in selector.text:
                    html = item.html
                    if html and pattern.regex.search(html):
                        detections.append(
                            Detection(
                                url=har.url,
                                fingerprint=fingerprint,
                                app_type="dom",
                                pattern=pattern,
                                value=html,
                            )
                        )

            if selector.attributes:
                for name, patterns in list(selector.attributes.items()):
                    content = item.attributes.get(name)
                    if not content:
                        continue

                    content = str(content)
                    for pattern in patterns:
                        if pattern.regex.search(content):
                            detections.append(
                                Detection(
                                    url=har.url,
                                    fingerprint=fingerprint,
                                    app_type="dom",
                                    pattern=pattern,
                                    value=content,
                                    key=name,
                                )
                            )

    return detections


def filter_by_requires(detections: list[Detection]) -> list[Detection]:
    filtered: list[Detection] = []

    detection_ids = {detection.fingerprint.id for detection in detections}
    for detection in detections:
        if not detection.fingerprint.requires:
            filtered.append(detection)
            continue

        if any(require in detection_ids for require in detection.fingerprint.requires):
            filtered.append(detection)

    return filtered


def filter_by_requires_category(detections: list[Detection]) -> list[Detection]:
    filtered: list[Detection] = []

    categories = set(
        itertools.chain.from_iterable(
            detection.fingerprint.cats for detection in detections
        )
    )
    for detection in detections:
        if not detection.fingerprint.requires_category:
            filtered.append(detection)
            continue

        if any(
            require in categories for require in detection.fingerprint.requires_category
        ):
            filtered.append(detection)

    return filtered


def filter_by_excludes(detections: list[Detection]) -> list[Detection]:
    excludes = set(
        itertools.chain.from_iterable(
            list(detection.fingerprint.excludes) for detection in detections
        )
    )
    return [
        detection
        for detection in detections
        if detection.fingerprint.id not in excludes
    ]


Analyze = Callable[[HarWrapper, schemas.Fingerprint], list[Detection]]


def set_categories(
    detections: list[Detection], *, categories: schemas.Categories
) -> list[Detection]:
    if not categories:
        return detections

    for detection in detections:
        memo: dict[str, schemas.Category] = {}

        for category_id in detection.fingerprint.cats:
            category = categories.root.get(str(category_id))
            if category:
                memo[category.id] = category

        if any(memo):
            detection.categories = list(memo.values())

    return detections


def set_groups(
    detections: list[Detection], *, groups: schemas.Groups
) -> list[Detection]:
    if not groups:
        return detections

    for detection in detections:
        memo: dict[str, schemas.Group] = {}

        if not detection.categories:
            continue

        for category in detection.categories:
            for group_id in category.groups:
                group = groups.root.get(str(group_id))
                if group:
                    memo[group.id] = group

        if any(memo):
            detection.groups = list(memo.values())

    return detections


class Wappalyzer:
    def __init__(
        self,
        fingerprints: schemas.Fingerprints | None = None,
        categories: schemas.Categories | None = None,
        groups: schemas.Groups | None = None,
    ):
        self.fingerprints = fingerprints or schemas.Fingerprints(root={})
        self.categories = categories or schemas.Categories(root={})
        self.groups = groups or schemas.Groups(root={})

    def analyze(self, har: schemas.Har | Any, *, analyzes: list[Analyze] | None = None):
        """Analyze HAR.

        Args:
            har (schemas.Har | Any): HAR.

        Returns:
            dict[str, dict[str, str]]: Technologies.
        """
        har = har if isinstance(har, schemas.Har) else schemas.Har.model_validate(har)
        wrapper = HarWrapper(log=har.log)

        analyzes = analyzes or [
            analyze_url,
            analyze_headers,
            analyze_cookies,
            analyze_scripts,
            analyze_css,
            analyze_meta,
            analyze_html,
            analyze_dom,
        ]
        detections = itertools.chain.from_iterable(
            itertools.chain.from_iterable(
                [
                    [analyze(wrapper, fingerprint) for analyze in analyzes]
                    for fingerprint in self.fingerprints.root.values()
                ]
            )
        )

        filtered = cast(
            list[Detection],
            pipe(
                list[Detection],
                filter_by_requires,
                filter_by_requires_category,
                filter_by_excludes,
            )(detections),
        )

        return cast(
            list[Detection],
            pipe(
                list[Detection],
                partial(set_categories, categories=self.categories),
                partial(set_groups, groups=self.groups),
            )(filtered),
        )
