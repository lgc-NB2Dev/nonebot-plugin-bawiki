import mimetypes
import re

import anyio
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from pil_utils.fonts import Font, get_proper_font
from playwright.async_api import Request, Route
from yarl import URL

from ..resource import BA_LOGO_JS_PATH, RES_DIR

RES_ROUTE_URL = "https://bawiki.res"
RES_TYPE_RESOURCE = "resource"
RES_TYPE_FONT = "font"


async def res_router(route: Route, request: Request):
    url = URL(request.url)
    logger.debug(f"Requested routed URL: {url.human_repr()}")

    parts = url.parts[1:]
    if not len(parts) >= 2:
        logger.debug("Invalid resource URL")
        return await route.abort()

    res_type = parts[0]
    res_path = "/".join(parts[1:])

    if res_type not in (RES_TYPE_RESOURCE, RES_TYPE_FONT):
        logger.debug(f"Invalid resource type `{res_type}` in URL")
        return await route.abort()

    if res_type == RES_TYPE_RESOURCE:
        path = anyio.Path(RES_DIR / res_path)
        mime = mimetypes.guess_type(path)[0]

        if not await path.exists():
            logger.debug(f"Resource `{res_path}` not found")
            return await route.abort()

    else:  # RES_TYPE_FONT
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

    logger.debug(
        f"Resolved {res_type} `{res_path}`, mimetype: {mime}, real path: {path}",
    )
    return await route.fulfill(body=await path.read_bytes(), content_type=mime)


async def get_logo(text_l: str, text_r: str, transparent_bg: bool = True) -> str:
    async with get_new_page() as page:
        await page.route(re.compile(f"^{RES_ROUTE_URL}/(.*)$"), res_router)
        await page.goto(f"{RES_ROUTE_URL}/{RES_TYPE_RESOURCE}/web/empty.html")
        return await page.evaluate(
            BA_LOGO_JS_PATH.read_text(encoding="u8"),
            [text_l, text_r, transparent_bg],
        )
