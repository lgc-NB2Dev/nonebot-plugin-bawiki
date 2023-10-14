import mimetypes
import re
from typing import TYPE_CHECKING

import anyio
from nonebot import logger, on_shell_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace
from nonebot_plugin_htmlrender import get_new_page
from pil_utils.fonts import Font, get_proper_font
from playwright.async_api import Request, Route
from yarl import URL

from ..help import FT_E, FT_S
from ..resource import RES_BA_LOGO_JS_PATH, RES_PATH

if TYPE_CHECKING:
    from . import HelpList


help_list: "HelpList" = [
    {
        "func": "标题生成器",
        "trigger_method": "指令",
        "trigger_condition": "balogo",
        "brief_des": "生成 BA Logo 样式的图片",
        "detail_des": (
            "生成 BA Logo 样式的图片\n"
            "感谢 nulla2011/Bluearchive-logo 项目以 MIT 协议开源了图片绘制代码\n"
            " \n"
            "可以用这些指令触发：\n"
            f"- {FT_S}balogo{FT_E}\n"
            f"- {FT_S}baLogo{FT_E}\n"
            f"- {FT_S}baLOGO{FT_E}\n"
            f"- {FT_S}ba标题{FT_E}\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}balogo Blue Archive{FT_E}\n"
            f"- {FT_S}balogo -T Schale SenSei{FT_E}（使用参数 -T 加上背景）\n"
            f'- {FT_S}balogo "我是" "秦始皇"{FT_E}（包含空格的文本请使用引号包裹）'
        ),
    },
]


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
        path = anyio.Path(RES_PATH / res_path)
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
            RES_BA_LOGO_JS_PATH.read_text(encoding="u8"),
            [text_l, text_r, (not transparent_bg)],
        )


parser = ArgumentParser("balogo", add_help=False)
parser.add_argument("text_l")
parser.add_argument("text_r")
parser.add_argument("-T", "--no-transparent", action="store_true")

cmd_ba_logo = on_shell_command(
    "balogo",
    aliases={"baLogo", "baLOGO", "ba标题"},
    parser=parser,
)


@cmd_ba_logo.handle()
async def _(matcher: Matcher, err: ParserExit = ShellCommandArgs()):
    if err.message:
        await matcher.finish(f"参数解析失败：{err.message}")


@cmd_ba_logo.handle()
async def _(matcher: Matcher, arg: Namespace = ShellCommandArgs()):
    try:
        b64_url = await get_logo(arg.text_l, arg.text_r, arg.no_transparent)
    except Exception:
        logger.exception("Error when generating image")
        await matcher.finish("遇到错误，请检查后台输出")
    await matcher.finish(MessageSegment.image(b64_url))
