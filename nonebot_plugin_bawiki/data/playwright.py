import mimetypes
import re
from contextlib import asynccontextmanager
from typing import AsyncIterator

import anyio
from httpx import Response
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from pil_utils.fonts import Font, get_proper_font
from playwright.async_api import Page, Request, Route
from yarl import URL

from ..resource import RES_DIR
from ..util import RespType, async_req

RES_ROUTE_URL = "https://bawiki.res"
RES_TYPE_RESOURCE = "resource"
RES_TYPE_FONT = "font"
RES_TYPE_URL = "url"


async def res_router(route: Route, request: Request):
    url = URL(request.url)
    logger.debug(f"Requested routed URL: {url.human_repr()}")

    parts = url.parts[1:]
    if not len(parts) >= 2:
        logger.debug("Invalid resource URL")
        return await route.abort()

    res_type = parts[0]
    res_path = "/".join(parts[1:])

    if res_type == RES_TYPE_RESOURCE:
        path = anyio.Path(RES_DIR / res_path)
        mime = mimetypes.guess_type(path)[0]

        if not await path.exists():
            logger.debug(f"Resource `{res_path}` not found")
            return await route.abort()

    elif res_type == RES_TYPE_FONT:
        family = res_path.replace("-", " ")
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

        path = anyio.Path(font.path)
        mime = f"font/{path.suffix[1:]}"

    elif res_type == RES_TYPE_URL:
        try:
            resp: Response = await async_req(res_path, resp_type=RespType.RESPONSE)
        except Exception as e:
            logger.debug(
                f"Request {res_type} `{res_path}` failed: "
                f"{e.__class__.__name__}: {e}",
            )
            return await route.abort()

        mime = resp.headers["Content-Type"] or "application/octet-stream"
        data = resp.read()

        logger.debug(f"Requested {res_type} `{res_path}`, mimetype: {mime}")
        return await route.fulfill(body=data, content_type=mime)

    else:
        logger.debug(f"Invalid resource type `{res_type}` in URL")
        return await route.abort()

    logger.debug(
        f"Resolved {res_type} `{res_path}`, mimetype: {mime}, real path: {path}",
    )
    return await route.fulfill(body=await path.read_bytes(), content_type=mime)


@asynccontextmanager
async def get_routed_page(**kwargs) -> AsyncIterator[Page]:
    async with get_new_page(**kwargs) as page:
        await page.route(re.compile(f"^{RES_ROUTE_URL}/(.*)$"), res_router)
        yield page
