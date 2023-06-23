import asyncio
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..data.bawiki import db_wiki_time_atk
from ..data.schaledb import find_current_event, schale_get_common
from ..util import splice_msg

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "综合战术考试一图流",
        "trigger_method": "指令",
        "trigger_condition": "ba综合战术考试",
        "brief_des": "查询综合战术考试攻略图",
        "detail_des": (
            "发送当前或指定综合战术考试一图流攻略图\n"
            "图片作者 B站@夜猫咪喵喵猫\n"
            " \n"
            "指令默认发送日服和国际服当前的综合战术考试攻略\n"
            "指令后面跟`日`或`j`开头的文本代表查询日服当前综合战术考试攻略，带以`国`或`g`开头的文本同理\n"
            "跟整数则代表指定第几个综合战术考试\n"
            " \n"
            "p.s. 综合战术考试 和 合同火力演习 其实是一个东西，国际服叫前者，日服叫后者～\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>ba综合战术考试</ft>\n"
            "- <ft color=(238,120,0)>ba合同火力演习</ft>\n"
            "- <ft color=(238,120,0)>ba战术考试</ft>\n"
            "- <ft color=(238,120,0)>ba火力演习</ft>\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba综合战术考试</ft>\n"
            "- <ft color=(238,120,0)>ba综合战术考试 日</ft>\n"
            "- <ft color=(238,120,0)>ba综合战术考试 8</ft>"
        ),
    },
]


cmd_time_atk_wiki = on_command("ba综合战术考试", aliases={"ba合同火力演习", "ba战术考试", "ba火力演习"})


@cmd_time_atk_wiki.handle()
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
                raid = common["regions"][s]["current_raid"]
                if (r := find_current_event(raid)) and (raid := r[0]["raid"]) >= 1000:
                    events.append(raid)
        except:
            logger.exception("获取当前综合战术考试失败")
            await matcher.finish("获取当前综合战术考试失败")

        if not events:
            await matcher.finish("当前服务器没有正在进行的综合战术考试")

    else:
        if (not str(arg).isdigit()) or ((arg := int(arg)) < 1):
            await matcher.finish("综合战术考试ID需为整数，从1开始，代表第1个综合战术考试")
        events.append(arg)

    try:
        ret = await asyncio.gather(*[db_wiki_time_atk(x) for x in events])
    except:
        logger.exception("获取综合战术考试wiki出错")
        await matcher.finish("获取图片出错，请检查后台输出")

    await matcher.finish(splice_msg(ret))
