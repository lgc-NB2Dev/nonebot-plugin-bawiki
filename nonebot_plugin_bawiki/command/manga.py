import asyncio
import random
from io import BytesIO
from typing import TYPE_CHECKING, List

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, EventMessage
from nonebot.typing import T_State
from pil_utils import BuildImage

from ..config import config
from ..data.gamekee import MangaMetadata, get_manga_content, get_manga_list
from ..help import FT_E, FT_S
from ..util import (
    IllegalOperationFinisher,
    RespType as Rt,
    async_req,
    send_forward_msg,
    split_list,
)

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
            "不带参数时，会从所有漫画中随机抽取一话发送\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba漫画{FT_E}\n"
            f"- {FT_S}ba漫画 蔚蓝档案四格漫画{FT_E}\n"
            f"- {FT_S}ba漫画 布噜布噜档案 第一话{FT_E}"
        ),
    },
]


KEY_MANGA_LIST = "manga_list"
KEY_SELECTED_MANGA = "selected_manga"

illegal_finisher = IllegalOperationFinisher("非法操作次数过多，已退出选择")

cmd_random_manga = on_command("ba漫画")


@cmd_random_manga.handle()
async def _(matcher: Matcher, state: T_State, arg_msg: Message = CommandArg()):
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

    manga_total = len(manga_list)
    state[KEY_MANGA_LIST] = manga_list
    if manga_total == 1:
        state[KEY_SELECTED_MANGA] = manga_list[0]
    elif not arg:
        index = random.randint(0, manga_total - 1)
        state[KEY_SELECTED_MANGA] = manga_list[index]
    else:
        if manga_total > 5:
            manga_list = manga_list[:5]
            state[KEY_MANGA_LIST] = manga_list
        list_msg = "\n".join(
            f"{i}. 【{x.category}】{x.name}" for i, x in enumerate(manga_list, 1)
        )
        too_much_tip = "\nTip：结果过多，仅显示前五个" if manga_total > 5 else ""
        await matcher.pause(
            f"找到了多个结果，请发送序号选择，发送 0 退出选择：\n{list_msg}{too_much_tip}",
        )


@cmd_random_manga.handle()
async def _(matcher: Matcher, state: T_State, message: Message = EventMessage()):
    if KEY_SELECTED_MANGA in state:
        return

    arg = message.extract_plain_text().strip()
    if arg == "0":
        await matcher.finish("已退出选择")

    index = int(arg) if arg.isdigit() else None
    manga_list: List[MangaMetadata] = state[KEY_MANGA_LIST]
    if (not index) or (index > len(manga_list)):
        await illegal_finisher()
        await matcher.reject("请输入正确的序号")

    state[KEY_SELECTED_MANGA] = manga_list[index - 1]


@cmd_random_manga.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    state: T_State,
):
    manga: MangaMetadata = state[KEY_SELECTED_MANGA]

    async def get_pic(url: str):
        p = await async_req(url, resp_type=Rt.BYTES)
        if url.endswith(".webp"):
            p = BuildImage.open(BytesIO(p)).save_png()
        return p

    try:
        content = await get_manga_content(manga.cid)
        pics = await asyncio.gather(*[get_pic(x) for x in content.images])
    except Exception:
        logger.exception(f"获取 CID {manga.cid} 漫画失败")
        await matcher.finish("获取漫画失败，请检查后台输出")

    image_sum = len(pics)
    image_seg = [MessageSegment.image(x) for x in pics]
    if (not config.ba_use_forward_msg) or image_sum <= 2:
        header = (
            f"https://ba.gamekee.com/{manga.cid}.html\n"
            f"【{manga.category}】{content.title}"
        )
        if content.content:
            header = f"{header}\n\n{content.content}"

        chunks = list(split_list(image_seg, 9))
        max_page = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            msg = Message()
            if i == 1:
                msg += header
            msg += chunk
            if max_page > 1:
                msg += f"第 {i} / {max_page} 页（共 {image_sum} P）"
            await matcher.send(msg)
        return

    headers = [Message() + f"【{manga.category}】{content.title}"]
    if content.content:
        headers.append(Message() + content.content)
    images = [Message(x) for x in image_seg]
    footer = Message() + f"https://ba.gamekee.com/{manga.cid}.html"
    await send_forward_msg(bot, event, [*headers, *images, footer])
