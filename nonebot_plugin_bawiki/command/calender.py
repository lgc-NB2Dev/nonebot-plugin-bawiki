import asyncio
from typing import TYPE_CHECKING, List, Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    ActionFailed,
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
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
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    cmd_arg: Message = CommandArg(),
):
    arg: str = cmd_arg.extract_plain_text()

    if "s" not in (arg := arg.lower()):
        # gamekee
        task = game_kee_calender()
    else:
        # schale
        servers = []
        if any(x in arg for x in ("日", "j")):
            servers.append(0)
        if any(x in arg for x in ("国", "g")):
            servers.append(1)
        task = asyncio.gather(*(schale_calender(x) for x in servers))

    await matcher.send("正在绘制图片，请稍等")
    try:
        messages: Union[List[MessageSegment], str] = await task
    except Exception:
        logger.exception("绘制日程表图片出错")
        await matcher.finish("绘制日程表图片出错，请检查后台输出")

    if isinstance(messages, str):
        await matcher.finish(messages)

    try:
        forward_nodes: List[MessageSegment] = [
            MessageSegment.node_custom(int(bot.self_id), "BAWiki", Message(x))
            for x in messages
        ]
        if isinstance(event, GroupMessageEvent):
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                messages=forward_nodes,
            )
        else:
            await bot.send_private_forward_msg(
                user_id=event.user_id,
                messages=forward_nodes,
            )
    except ActionFailed:
        logger.warning("以合并转发形式发送失败，尝试使用普通方式发送")
        await matcher.finish(Message(messages))
