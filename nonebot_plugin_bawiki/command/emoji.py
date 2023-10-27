import random
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher

from ..data.bawiki import db_get, db_get_emoji
from ..util import RespType

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "抽表情",
        "trigger_method": "指令",
        "trigger_condition": "ba表情",
        "brief_des": "随机发送一个国际服社团聊天表情",
        "detail_des": "随机发送一个国际服社团聊天表情\n来源：解包",
    },
]


cmd_random_emoji = on_command("ba表情")


@cmd_random_emoji.handle()
async def _(matcher: Matcher):
    try:
        emojis = await db_get_emoji()
        emo = await db_get(random.choice(emojis), resp_type=RespType.BYTES)
    except Exception:
        logger.exception("获取表情失败")
        await matcher.finish("获取表情失败，请检查后台输出")
    await matcher.finish(MessageSegment.image(emo))
