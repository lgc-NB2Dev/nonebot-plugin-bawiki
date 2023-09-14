import asyncio
import random
from io import BytesIO
from typing import TYPE_CHECKING, List

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg
from pil_utils import BuildImage

from ..data.gamekee import get_manga_content, get_manga_list
from ..help import FT_E, FT_S
from ..util import async_req

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "随机漫画",
        "trigger_method": "指令",
        "trigger_condition": "ba漫画",
        "brief_des": "发送一话官推/同人漫画",
        "detail_des": (
            "从GameKee爬取BA官推/同人漫画并发送\n"
            "可以使用GameKee主页漫画图书馆的漫画名字和链接标题搜索\n"
            "搜索到多个结果时，会从搜到的结果中随机选择一个发送\n"
            "不带参数时，会从所有漫画中随机抽取一话发送\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba漫画{FT_E}\n"
            f"- {FT_S}ba漫画 蔚蓝档案四格漫画{FT_E}\n"
            f"- {FT_S}ba漫画 布噜布噜档案 第一话{FT_E}"
        ),
    },
]


cmd_random_manga = on_command("ba漫画")


@cmd_random_manga.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    arg_msg: Message = CommandArg(),
):
    async def get_pic(url):
        p = await async_req(url, raw=True)
        if url.endswith(".webp"):
            p = BuildImage.open(BytesIO(p)).save_png()
        return p

    try:
        manga_list = await get_manga_list()
    except Exception:
        logger.exception("获取漫画列表失败")
        await matcher.finish("获取漫画列表失败，请检查后台输出")

    arg = arg_msg.extract_plain_text().strip().split()
    if arg:
        manga_list = [
            x
            for x in manga_list
            if all((kw in x.category or kw in x.name) for kw in arg)
        ]

    if not manga_list:
        await matcher.finish("未找到对应关键词的漫画")

    manga = random.choice(manga_list) if len(manga_list) > 1 else manga_list[0]
    try:
        content = await get_manga_content(manga.cid)
        pics = await asyncio.gather(*[get_pic(x) for x in content.images])
    except Exception:
        logger.exception(f"获取 CID {manga.cid} 漫画失败")
        await matcher.finish("获取漫画失败，请检查后台输出")

    image_seg = [MessageSegment.image(x) for x in pics]
    if len(pics) <= 2:
        await matcher.finish(
            Message()
            + (
                f"【{manga.category}】{content.title}\n"
                "-=-=-=-=-=-=-=-\n"
                f"{content.content}"
            )
            + image_seg
            + f"-=-=-=-=-=-=-=-\nhttps://ba.gamekee.com/{manga.cid}.html",
        )

    headers = [Message() + f"【{manga.category}】{content.title}"]
    if content.content:
        headers.append(Message() + content.content)
    images = [Message(x) for x in image_seg]
    footer = Message() + f"https://ba.gamekee.com/{manga.cid}.html"

    nodes: List[MessageSegment] = [
        MessageSegment.node_custom(int(bot.self_id), "BAWiki", x)
        for x in (*headers, *images, footer)
    ]
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(group_id=event.group_id, messages=nodes)
    else:
        await bot.send_private_forward_msg(user_id=event.user_id, messages=nodes)
