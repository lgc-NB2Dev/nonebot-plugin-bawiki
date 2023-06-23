import asyncio
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..data.bawiki import db_get_event_alias, db_wiki_event
from ..data.schaledb import find_current_event, schale_get_common
from ..util import recover_alia, splice_msg

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "活动一图流",
        "trigger_method": "指令",
        "trigger_condition": "ba活动",
        "brief_des": "查询活动攻略图",
        "detail_des": (
            "发送当前或指定活动一图流攻略图，可能会附带活动特殊机制等\n"
            "图片作者 B站@夜猫咪喵喵猫\n"
            " \n"
            "指令默认发送日服和国际服当前的活动攻略\n"
            "指令后面跟`日`或`j`开头的文本代表查询日服当前活动攻略，带以`国`或`g`开头的文本同理\n"
            "跟其他文本则代表指定活动名称\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba活动</ft>\n"
            "- <ft color=(238,120,0)>ba活动 日</ft>\n"
            "- <ft color=(238,120,0)>ba活动 温泉浴场</ft>"
        ),
    },
]


cmd_event_wiki = on_command("ba活动")


@cmd_event_wiki.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().lower().strip()

    server = []
    if arg.startswith(("日", "j")) or not arg:
        server.append(0)
    if arg.startswith(("国", "g")) or not arg:
        server.append(1)

    events = []
    if server:
        try:
            common = await schale_get_common()
            for s in server:
                ev = common["regions"][s]["current_events"]
                if e := find_current_event(ev):
                    events.append((e[0]["event"]) % 10000)
        except:
            logger.exception("获取当前活动失败")
            await matcher.finish("获取当前活动失败")

        if not events:
            await matcher.finish("当前服务器没有正在进行的活动")

    else:
        events.append(recover_alia(arg, await db_get_event_alias()))

    try:
        ret = await asyncio.gather(*[db_wiki_event(x) for x in events])
    except:
        logger.exception("获取活动wiki出错")
        await matcher.finish("获取图片出错，请检查后台输出")

    await matcher.finish(splice_msg(ret))
