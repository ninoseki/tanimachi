from functools import cached_property

from pydantic import AnyUrl, AwareDatetime, BaseModel, Field

from .api_model import APIModel
from .mixins import FileMixin


class Creator(BaseModel):
    name: str
    version: str
    comment: str | None = None


class Browser(BaseModel):
    name: str
    version: str
    comment: str | None = None


class PageTimings(APIModel):
    on_content_load: float | None = None
    on_load: float | None = None
    comment: str | None = None


class Cookie(APIModel):
    name: str
    value: str
    path: str | None = None
    domain: str | None = None
    expires: AwareDatetime | None = None
    http_only: bool | None = None
    secure: bool | None = None
    comment: str | None = None


class Header(BaseModel):
    name: str
    value: str
    comment: str | None = None


class Query(BaseModel):
    name: str
    value: str
    comment: str | None = None


class Params(APIModel):
    name: str
    value: str | None = None
    file_name: str | None = None
    content_type: str | None = None
    comment: str | None = None


class PostData(APIModel):
    mime_type: str
    text: str | None = None
    params: list | Params | None = None
    comment: str | None = None


class Content(APIModel):
    size: int
    compression: int | None = None
    mime_type: str
    text: str | None = None
    encoding: str | None = None
    comment: str | None = None


class BeforeAfterRequest(APIModel):
    expires: str | None = None
    last_access: str
    e_tag: str
    hit_count: int
    comment: str | None = None


class Timings(BaseModel):
    dns: float | None = None
    connect: float | None = None
    blocked: float | None = None
    send: float
    wait: float
    receive: float
    ssl: float | None = None
    comment: str | None = None


class Page(APIModel):
    started_date_time: AwareDatetime
    id: str
    title: str
    page_timings: PageTimings
    comment: str | None = None


class Request(APIModel):
    method: str
    url: AnyUrl
    http_version: str
    cookies: list[Cookie]
    headers: list[Header]
    query_string: list[Query]
    post_data: PostData | None = None
    headers_size: int
    body_size: int
    comment: str | None = None


class Response(APIModel):
    status: int
    status_text: str
    http_version: str
    cookies: list[Cookie]
    headers: list[Header]
    content: Content
    redirect_url: str = Field(..., alias="redirectURL")
    headers_size: int
    body_size: int
    comment: str | None = None


class Cache(APIModel):
    before_request: BeforeAfterRequest | None = None
    after_request: BeforeAfterRequest | None = None
    comment: str | None = None


class Entry(APIModel):
    pageref: str | None = None
    started_date_time: AwareDatetime
    time: float
    request: Request
    response: Response
    cache: Cache
    timings: Timings
    server_ip_address: str | None = Field(None, alias="serverIPAddress")
    connection: str | None = None
    comment: str | None = None

    @cached_property
    def headers(self) -> dict[str, str]:
        return {header.name: header.value for header in self.response.headers}

    @cached_property
    def cookies(self) -> dict[str, str]:
        return {header.name: header.value for header in self.response.cookies}


class Log(BaseModel):
    version: str
    creator: Creator
    browser: Browser | None = None
    pages: list[Page] | None = None
    entries: list[Entry]
    comment: str | None = None


class Har(FileMixin):
    log: Log
