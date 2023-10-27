import asyncio
import random
from io import BytesIO
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg
from pil_utils import BuildImage

from ..config import config
from ..data.gamekee import get_manga_content, get_manga_list
from ..help import FT_E, FT_S
from ..util import RespType, async_req, send_forward_msg, split_list

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
        p = await async_req(url, resp_type=RespType.BYTES)
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

    image_sum = len(pics)
    image_seg = [MessageSegment.image(x) for x in pics]
    if (not config.ba_use_forward_msg) or image_sum < 2:
        header = (
            f"https://ba.gamekee.com/{manga.cid}.html\n"
            f"【{manga.category}】{content.title}"
        )
        if content.content:
            header = f"{header}\n\n{content.content}"

        sem = asyncio.Semaphore(2)

        async def send(msg):
            async with sem:
                await matcher.send(msg)

        chunks = list(split_list(image_seg, 9))
        max_page = len(chunks)
        tasks = []
        for i, chunk in enumerate(chunks, 1):
            msg = Message()
            if i == 1:
                msg += header
            msg += chunk
            if max_page > 1:
                msg += f"第 {i} / {max_page} 页（共 {image_sum} P）"
            tasks.append(send(msg))

        await asyncio.gather(*tasks)
        return

    headers = [Message() + f"【{manga.category}】{content.title}"]
    if content.content:
        headers.append(Message() + content.content)
    images = [Message(x) for x in image_seg]
    footer = Message() + f"https://ba.gamekee.com/{manga.cid}.html"
    await send_forward_msg(bot, event, [*headers, *images, footer])
