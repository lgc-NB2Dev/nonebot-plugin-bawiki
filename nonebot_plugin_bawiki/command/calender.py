import asyncio
from typing import TYPE_CHECKING, List, Literal

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..config import config
from ..data.gamekee import game_kee_calender
from ..data.schaledb import schale_calender
from ..help import FT_E, FT_S
from ..util import send_forward_msg

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "日程表",
        "trigger_method": "指令",
        "trigger_condition": "ba日程表",
        "brief_des": "查看活动日程表",
        "detail_des": (
            "查看当前未结束的卡池、活动以及起止时间\n"
            "默认展示来自GameKee源的所有服务器日程\n"
            "可以使用下方的指令参数指定数据源和展示的服务器\n"
            " \n"
            "可以在指令后带参数，每个参数请使用空格分隔\n"
            "参数列表：\n"
            "- 使用SchaleDB数据源：\n"
            f"  {FT_S}夏莱{FT_E} / {FT_S}沙勒{FT_E} / {FT_S}s{FT_E} / {FT_S}schale{FT_E} / {FT_S}schaledb{FT_E}\n"
            "- 展示日服日程：\n"
            f"  {FT_S}日{FT_E} / {FT_S}日服{FT_E} / {FT_S}j{FT_E} / {FT_S}jp{FT_E} / {FT_S}japan{FT_E}\n"
            "- 展示国际服日程：\n"
            f"  {FT_S}国际{FT_E} / {FT_S}国际服{FT_E} / {FT_S}g{FT_E} / {FT_S}gl{FT_E} / {FT_S}global{FT_E}\n"
            "- 展示国服日程：\n"
            f"  {FT_S}国服{FT_E} / {FT_S}c{FT_E} / {FT_S}cn{FT_E} / {FT_S}china{FT_E} / {FT_S}chinese{FT_E}\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba日程表{FT_E} （GameKee源）\n"
            f"- {FT_S}ba日程表 schale{FT_E} （SchaleDB源，所有服务器）\n"
            f"- {FT_S}ba日程表 schale 日服 国际服{FT_E} （SchaleDB源，日服和国际服）"
        ),
    },
]


cmd_calender = on_command("ba日程表")


@cmd_calender.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    cmd_arg: Message = CommandArg(),
):
    args: List[str] = cmd_arg.extract_plain_text().strip().lower().split()

    gamekee = True
    servers: List[Literal["Jp", "Global", "Cn"]] = []

    if any((x in ("夏莱", "沙勒", "s", "schale", "schaledb")) for x in args):
        gamekee = False
    if any((x in ("日", "日服", "j", "jp", "japan")) for x in args):
        servers.append("Jp")
    if any((x in ("国际", "国际服", "g", "gl", "global")) for x in args):
        servers.append("Global")
    if any((x in ("国服", "c", "cn", "china", "chinese")) for x in args):
        servers.append("Cn")

    if not servers:
        servers = ["Jp", "Global", "Cn"]

    if gamekee:
        task = game_kee_calender(servers)
    else:
        task = asyncio.gather(*(schale_calender(x) for x in servers))

    await matcher.send("正在绘制图片，请稍等")
    try:
        pics = await task
    except Exception:
        logger.exception("绘制日程表图片出错")
        await matcher.finish("绘制日程表图片出错，请检查后台输出")

    if not pics:
        await matcher.finish("没有获取到日程表数据")

    messages = [MessageSegment.image(x) for x in pics]

    if config.ba_use_forward_msg:
        await send_forward_msg(bot, event, messages)
        return

    await matcher.finish(Message(messages))
