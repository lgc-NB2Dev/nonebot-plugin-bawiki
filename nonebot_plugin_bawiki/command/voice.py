import random
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..config import config
from ..data.bawiki import recover_stu_alia, schale_to_gamekee
from ..data.gamekee import GameKeeVoice, game_kee_get_stu_li, game_kee_get_voice
from ..help import FT_E, FT_S
from ..util import async_req

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "学生语音",
        "trigger_method": "指令",
        "trigger_condition": "ba语音",
        "brief_des": "发送学生语音",
        "detail_des": (
            "从GameKee爬取学生语音并发送\n"
            "可以用 语音名称 或 中文或日文台词 搜索角色语音\n"
            "如果有多个结果，则会从中随机选择一个语音发送\n"
            " \n"
            "默认获取日配语音，如果角色有中配，则可以在指令后方带上 `中配` 来获取\n"
            "如果找不到中配语音对应的台词，则会展示日配台词\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba语音 忧{FT_E}\n"
            f"- {FT_S}ba语音 美游 被cc{FT_E}\n"
            f"- {FT_S}ba语音 水大叔 好热{FT_E}\n"
            f"- {FT_S}ba语音中配 白子{FT_E}\n"
            f"- {FT_S}ba语音中配 大叔 睡午觉{FT_E}"
        ),
    },
]


cmd_voice = on_command("ba语音")


@cmd_voice.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    is_chinese = False
    if arg.startswith("中配"):
        arg = arg[2:].strip()
        is_chinese = True

    if not arg:
        await matcher.finish("请提供学生名称")

    arg = arg.split()
    arg_len = len(arg)
    name = " ".join(arg[:-1]) if arg_len > 1 else arg[0]
    v_type = arg[-1].strip().lower() if arg_len > 1 else None

    try:
        ret = await game_kee_get_stu_li()
    except Exception:
        logger.exception("获取学生列表出错")
        await matcher.finish("获取学生列表出错，请检查后台输出")

    if not ret:
        await matcher.finish("没有获取到学生列表数据")

    try:
        org_stu_name = await recover_stu_alia(name, game_kee=True)
        stu_name = await schale_to_gamekee(org_stu_name)
    except Exception:
        logger.exception("还原学生别名失败")
        await matcher.finish("还原学生别名失败，请检查后台输出")

    if not (stu_info := ret.get(stu_name)):
        await matcher.finish("未找到该学生")

    voices = await game_kee_get_voice(stu_info["content_id"], is_chinese)
    if v_type:
        voices = [
            x
            for x in voices
            if (
                (v_type in x.title.lower())
                or (v_type in x.jp.lower())
                or (v_type in x.cn.lower())
            )
        ]
    if not voices:
        await matcher.finish("没找到符合要求的语音捏")

    v: GameKeeVoice = random.choice(voices)
    voice_type = "中配" if is_chinese else "日配"
    im = [f"学生 {org_stu_name} {voice_type}语音 {v.title}"]
    if v.jp or v.cn:
        im.append("-=-=-=-=-=-=-=-")
        if v.jp:
            im.append(v.jp)
        if v.cn:
            im.append(v.cn)
    await matcher.send("\n".join(im))

    if config.ba_voice_use_card:
        await matcher.finish(
            MessageSegment(
                "music",
                {
                    "type": "custom",
                    "subtype": "163",
                    "url": v.url,
                    "voice": v.url,
                    "title": v.title,
                    "content": org_stu_name,
                    "image": f'http:{stu_info["icon"]}',
                },
            ),
        )

    v_data = await async_req(v.url, raw=True)
    await matcher.finish(MessageSegment.record(v_data))
