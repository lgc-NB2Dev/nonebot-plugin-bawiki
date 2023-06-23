from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.matcher import Matcher
from nonebot.log import logger

from ..data.bawiki import db_wiki_craft

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "制造一图流",
        "trigger_method": "指令",
        "trigger_condition": "ba制造",
        "brief_des": "查询制造功能机制图",
        "detail_des": (
            "发送游戏内制造功能的一图流介绍\n"
            "图片作者 B站@夜猫咪喵喵猫\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>ba制造</ft>\n"
            "- <ft color=(238,120,0)>ba制作</ft>\n"
            "- <ft color=(238,120,0)>ba合成</ft>"
        ),
    },
]


cmd_craft_wiki = on_command("ba制造", aliases={"ba合成", "ba制作"})


@cmd_craft_wiki.handle()
async def _(matcher: Matcher):
    try:
        im = await db_wiki_craft()
    except:
        logger.exception("获取合成wiki图片错误")
        await matcher.finish("获取图片失败，请检查后台输出")

    await matcher.finish(Message(im))
