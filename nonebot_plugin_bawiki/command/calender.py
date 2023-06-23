import asyncio
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import ActionFailed, Message
from nonebot.exception import FinishedException
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..data.gamekee import game_kee_calender
from ..data.schaledb import schale_calender

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "日程表",
        "trigger_method": "指令",
        "trigger_condition": "ba日程表",
        "brief_des": "查看活动日程表",
        "detail_des": (
            "查看当前未结束的卡池、活动以及起止时间，"
            "默认为GameKee源，可以在指令后带参数使用SchaleDB数据源\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba日程表</ft> （GameKee源）\n"
            "- <ft color=(238,120,0)>ba日程表 schaledb</ft> （SchaleDB源，日服国际服一起发）\n"
            "- <ft color=(238,120,0)>ba日程表 schale 国际服</ft> （SchaleDB源，国际服）"
        ),
    },
]


cmd_calender = on_command("ba日程表")


@cmd_calender.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg: str = cmd_arg.extract_plain_text()

    await matcher.send("正在绘制图片，请稍等")
    try:
        if "s" in (arg := arg.lower()):
            arg = arg.replace("schale", "").strip()
            servers = []

            if (not arg) or ("日" in arg) or ("j" in arg):
                servers.append(0)
            if (not arg) or ("国" in arg) or ("g" in arg):
                servers.append(1)

            await asyncio.gather(
                *[
                    matcher.send(x)
                    for x in (
                        await asyncio.gather(*[schale_calender(x) for x in servers])
                    )
                ],
            )
            await matcher.finish()
        else:
            await matcher.finish(await game_kee_calender())
    except (FinishedException, ActionFailed):  # type: ignore
        raise
    except:
        logger.exception("绘制日程表图片出错")
        await matcher.finish("绘制日程表图片出错，请检查后台输出")
