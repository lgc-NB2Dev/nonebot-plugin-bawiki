import mimetypes
import re
from contextlib import asynccontextmanager
from typing import AsyncIterator, Awaitable, Callable, Dict, TypeVar, Union

import anyio
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from pil_utils.fonts import Font, get_proper_font
from playwright.async_api import Page, Request, Route
from yarl import URL

from ..resource import EMPTY_HTML_PATH, RES_DIR

PWRouter = Callable[[Route, Request], Awaitable[None]]
BAWikiRouter = Callable[..., Awaitable[None]]
TRF = TypeVar("TRF", bound=BAWikiRouter)

RES_ROUTE_URL = "https://bawiki.res"
RES_TYPE_FONT = "font"


registered_routers: Dict[str, "BAWikiRouter"] = {}


def bawiki_router(path: str):
    def wrapper(func: TRF) -> TRF:
        registered_routers[path] = func
        return func

    return wrapper


async def route_page(page: Page, pattern: Union[str, re.Pattern], func: BAWikiRouter):
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern)

    async def wrapped(route: Route, request: Request):
        url = URL(request.url)
        logger.debug(f"Requested routed URL: {url.human_repr()}")
        match = re.search(pattern, request.url)
        assert match
        return await func(match=match, url=url, route=route, request=request)

    await page.route(re.compile(pattern), wrapped)


@asynccontextmanager
async def get_routed_page(**kwargs) -> AsyncIterator[Page]:
    async with get_new_page(**kwargs) as page:
        for k, v in registered_routers.items():
            await route_page(page, k, v)
        await page.goto(RES_ROUTE_URL)
        yield page


# region routers


@bawiki_router(rf"^{RES_ROUTE_URL}/?$")
async def _(route: Route, **_):
    html = EMPTY_HTML_PATH.read_text()
    return await route.fulfill(body=html, content_type="text/html")


@bawiki_router(rf"^{RES_ROUTE_URL}/{RES_TYPE_FONT}/(.+?)(\?.*)?$")
async def _(match: re.Match, url: URL, route: Route, **_):
    family = match.group(1).replace("-", " ")
    style = url.query.get("style", "normal")
    weight = url.query.get("weight", "normal")
    try:
        font = Font.find(
            family,
            style=style,
            weight=weight,
            fallback_to_default=False,
        )
    except Exception:
        logger.info(f"Font `{family}` not found, use fallback font")
        font = get_proper_font("国", style=style, weight=weight)  # type: ignore

    file_path = anyio.Path(font.path)
    mime = f"font/{file_path.suffix[1:]}"

    logger.debug(f"Resolved font `{family}`, file path: {file_path}")
    return await route.fulfill(body=await file_path.read_bytes(), content_type=mime)


@bawiki_router(rf"^{RES_ROUTE_URL}/(.+)$")
async def _(match: re.Match, route: Route, **_):
    res_path = match.group(1)
    file_path = anyio.Path(RES_DIR / res_path)

    if not await file_path.exists():
        logger.debug(f"Resource `{res_path}` not found")
        return await route.abort()

    mime = mimetypes.guess_type(file_path)[0]
    logger.debug(
        f"Resolved resource `{res_path}`, mimetype: {mime}, real path: {file_path}",
    )
    return await route.fulfill(body=await file_path.read_bytes(), content_type=mime)


# endregion
