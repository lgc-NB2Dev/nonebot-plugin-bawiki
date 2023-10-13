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
            f'- {FT_S}balogo "我是" "秦始皇"{FT_E}（包含空格的文本请使用引号包裹）'
        ),
    },
]


RES_ROUTE_PREFIX = "https://bawiki.res/"


async def res_router(route: Route, request: Request):
    res_name = URL(request.url).path[1:]
    logger.debug(f"Requested resource `{res_name}`")

    path = anyio.Path(RES_PATH / res_name)
    if not await path.exists():
        logger.debug(f"Resource `{res_name}` not found")
        await route.abort()
        return

    mime = mimetypes.guess_type(path)[0]
    logger.debug(f"Resource `{res_name}` mimetype: {mime}, path: {path}")
    await route.fulfill(body=await path.read_bytes(), content_type=mime)


async def get_logo(text_l: str, text_r: str) -> str:
    async with get_new_page() as page:
        await page.route(re.compile(f"^{RES_ROUTE_PREFIX}(.*)$"), res_router)
        await page.goto(f"{RES_ROUTE_PREFIX}web/empty.html")
        return await page.evaluate(
            RES_BA_LOGO_JS_PATH.read_text(encoding="u8"),
            [text_l, text_r],
        )


parser = ArgumentParser("balogo", add_help=False)
parser.add_argument("text_l")
parser.add_argument("text_r")

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
        b64_url = await get_logo(arg.text_l, arg.text_r)
    except Exception:
        logger.exception("Error when generating image")
        await matcher.finish("遇到错误，请检查后台输出")
    await matcher.finish(MessageSegment.image(b64_url))
