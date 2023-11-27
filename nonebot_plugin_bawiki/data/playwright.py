import mimetypes
import re
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
)

import anyio
import jinja2
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from pil_utils.fonts import Font, get_proper_font
from playwright.async_api import Page, Request, Route
from yarl import URL

from ..resource import EMPTY_HTML_PATH, RES_DIR

PWRouter = Callable[[Route, Request], Awaitable[None]]
BAWikiRouterFunc = Callable[..., Awaitable[None]]
TRF = TypeVar("TRF", bound=BAWikiRouterFunc)

RES_ROUTE_URL = "https://bawiki.res"
RES_TYPE_FONT = "font"


registered_routers: List["BAWikiRouter"] = []


@dataclass
class BAWikiRouter:
    pattern: Union[str, re.Pattern]
    func: BAWikiRouterFunc
    priority: int


def bawiki_router(
    pattern: Union[str, re.Pattern],
    flags: Optional[re.RegexFlag] = None,
    priority: int = 0,
):
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern, flags=flags or 0)

    def wrapper(func: TRF) -> TRF:
        registered_routers.append(BAWikiRouter(pattern, func, priority))
        # 低 priority 的 BAWikiRouter 应最先运行，
        # 因为 playwright 后 route 的先运行，所以要反过来排序
        registered_routers.sort(key=lambda r: r.priority, reverse=True)
        logger.debug(f"Registered router: {pattern=}, {priority=}")
        return func

    return wrapper


async def route_page(page: Page, router: BAWikiRouter):
    async def wrapped(route: Route, request: Request):
        url = URL(request.url)
        logger.debug(f"Requested routed URL: {url.human_repr()}")
        match = re.search(router.pattern, request.url)
        assert match
        return await router.func(match=match, url=url, route=route, request=request)

    await page.route(router.pattern, wrapped)


@asynccontextmanager
async def get_routed_page(**kwargs) -> AsyncIterator[Page]:
    async with get_new_page(**kwargs) as page:
        for router in registered_routers:
            await route_page(page, router)
        await page.goto(RES_ROUTE_URL)
        yield page


async def render_html(
    html: str,
    selector: str = "body",
    img_format: Literal["png", "jpeg"] = "jpeg",
    **page_kwargs,
) -> bytes:
    from pathlib import Path

    Path("debug.html").write_text(html, encoding="u8")

    async with get_routed_page(**page_kwargs) as page:
        await page.set_content(html)
        elem = await page.query_selector(selector)
        assert elem
        return await elem.screenshot(type=img_format)


def get_template_renderer(
    template: jinja2.Template,
    selector: str = "body",
    img_format: Literal["png", "jpeg"] = "jpeg",
    **page_kwargs,
) -> Callable[..., Awaitable[bytes]]:
    async def renderer(**template_kwargs) -> bytes:
        html = await template.render_async(**template_kwargs)
        return await render_html(html, selector, img_format, **page_kwargs)

    return renderer


# region routers


@bawiki_router(rf"^{RES_ROUTE_URL}/?$")
async def _(route: Route, **_):
    html = EMPTY_HTML_PATH.read_text()
    return await route.fulfill(body=html, content_type="text/html")


@bawiki_router(rf"^{RES_ROUTE_URL}/{RES_TYPE_FONT}/([^/]+?)/?$")
async def _(url: URL, route: Route, **_):
    family = url.parts[-1]
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


@bawiki_router(rf"^{RES_ROUTE_URL}/(.+)$", priority=99)
async def _(url: URL, route: Route, **_):
    res_path = url.parts[1:]
    file_path = anyio.Path(RES_DIR.joinpath(*res_path))

    if not await file_path.exists():
        logger.debug(f"Resource `{res_path}` not found")
        return await route.abort()

    mime = mimetypes.guess_type(file_path)[0]
    logger.debug(
        f"Resolved resource `{'/'.join(res_path)}`, mimetype: {mime}, real path: {file_path}",
    )
    return await route.fulfill(
        body=await file_path.read_bytes(),
        content_type=mime or "application/octet-stream",
    )


# endregion
