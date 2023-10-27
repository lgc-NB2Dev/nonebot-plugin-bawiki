from typing import TYPE_CHECKING

from nonebot import logger, on_shell_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace

from ..data.logo_generate import get_logo
from ..help import FT_E, FT_S

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
        b64_url = await get_logo(arg.text_l, arg.text_r, (not arg.no_transparent))
    except Exception:
        logger.exception("Error when generating image")
        await matcher.finish("遇到错误，请检查后台输出")
    await matcher.finish(MessageSegment.image(b64_url))
