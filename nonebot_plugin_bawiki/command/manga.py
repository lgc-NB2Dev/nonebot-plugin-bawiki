import asyncio
import random
from io import BytesIO
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from pil_utils import BuildImage

from ..data.bawiki import MangaDict, db_get_manga
from ..util import async_req

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "随机漫画",
        "trigger_method": "指令",
        "trigger_condition": "ba漫画",
        "brief_des": "随机发送一话官推漫画",
        "detail_des": "随机发送一话BA官推漫画\n来源：GameKee",
    },
]


cmd_random_manga = on_command("ba漫画")


@cmd_random_manga.handle()
async def _(matcher: Matcher):
    async def get_pic(url):
        p = await async_req(url, raw=True)
        if url.endswith(".webp"):
            p = BuildImage.open(BytesIO(p)).save_png()
        return p

    try:
        manga: MangaDict = random.choice(await db_get_manga())
        pics = await asyncio.gather(*[get_pic(x) for x in manga["pics"]])
    except:
        logger.exception("获取漫画失败")
        await matcher.finish("获取漫画失败，请检查后台输出")

    await matcher.finish(
        Message()
        + f'{manga["title"]}\n-=-=-=-=-=-=-=-\n{manga["detail"]}'
        + [MessageSegment.image(x) for x in pics],
    )
