from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..config import config
from ..data.bawiki import db_get_extra_l2d_list, recover_stu_alia, schale_to_gamekee
from ..data.gamekee import game_kee_get_stu_cid_li, game_kee_grab_l2d
from ..data.schaledb import draw_fav_li, schale_get_stu_dict
from ..util import async_req

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "羁绊查询",
        "trigger_method": "指令",
        "trigger_condition": "ba羁绊",
        "brief_des": "查询学生解锁L2D需求的羁绊等级",
        "detail_des": (
            "使用学生名称查询该学生解锁L2D看板需求的羁绊等级以及L2D预览，"
            "或者使用羁绊等级级数查询哪些学生达到该等级时解锁L2D看板\n"
            "使用学生名称查询时支持部分学生别名\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>ba羁绊</ft>\n"
            "- <ft color=(238,120,0)>ba好感度</ft>\n"
            "- <ft color=(238,120,0)>bal2d</ft>\n"
            "- <ft color=(238,120,0)>balive2d</ft>\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba羁绊 xcw</ft>\n"
            "- <ft color=(238,120,0)>ba羁绊 9</ft>"
        ),
    },
]


cmd_fav = on_command(
    "ba好感度",
    aliases={"ba羁绊", "bal2d", "baL2D", "balive2d", "baLive2D"},
)


@cmd_fav.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    async def get_l2d(stu_name):
        if r := (await db_get_extra_l2d_list()).get(stu_name):
            return [f"{config.ba_bawiki_db_url}{x}" for x in r]

        return await game_kee_grab_l2d((await game_kee_get_stu_cid_li()).get(stu_name))

    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        await matcher.finish("请提供学生名称或所需的羁绊等级")

    # 好感度等级
    if arg.isdigit():
        arg = int(arg)
        if arg > 9:
            await matcher.finish("学生解锁L2D最高只需要羁绊等级9")
        if arg < 1:
            await matcher.finish("学生解锁L2D最低只需要羁绊等级1")

        try:
            p = await draw_fav_li(arg)
        except:
            logger.exception("绘制图片出错")
            await matcher.finish("绘制图片出错，请检查后台输出")

        await matcher.finish(p)

    # 学生名称
    arg = await recover_stu_alia(arg)

    try:
        ret = await schale_get_stu_dict()
    except:
        logger.exception("获取学生列表出错")
        await matcher.finish("获取学生列表表出错，请检查后台输出")

    if stu := ret.get(arg):
        if not (lvl := stu["MemoryLobby"]):
            await matcher.finish("该学生没有L2D")

        im = MessageSegment.text(f'{stu["Name"]} 在羁绊等级 {lvl[0]} 时即可解锁L2D\nL2D预览：')
        if p := await get_l2d(await schale_to_gamekee(arg)):
            im += [MessageSegment.image(await async_req(x, raw=True)) for x in p]
        else:
            im += (
                "没找到该学生的L2D看板\n"
                "可能原因：\n"
                "- GameKee页面爬取不到角色L2D图片\n"
                "- GameKee和插件没有收录该学生的L2D\n"
            )
        await matcher.finish(im)

    await matcher.finish("未找到学生")
