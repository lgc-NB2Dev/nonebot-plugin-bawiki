import asyncio
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import ActionFailed, Message, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..config import config
from ..data.bawiki import db_get_extra_l2d_list, recover_stu_alia, schale_to_gamekee
from ..data.gamekee import game_kee_get_stu_cid_li, game_kee_grab_l2d
from ..data.schaledb import draw_fav_li, get_fav_li, schale_get_stu_dict
from ..help import FT_E, FT_S
from ..util import RespType as Rt, async_req

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
            f"- {FT_S}ba羁绊{FT_E}\n"
            f"- {FT_S}ba好感度{FT_E}\n"
            f"- {FT_S}bal2d{FT_E}\n"
            f"- {FT_S}balive2d{FT_E}\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba羁绊 xcw{FT_E}\n"
            f"- {FT_S}ba羁绊 9{FT_E}"
        ),
    },
]


cmd_fav = on_command(
    "ba好感度",
    aliases={"ba羁绊", "bal2d", "baL2D", "balive2d", "baLive2D"},
)


@cmd_fav.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    async def check_size(url: str) -> bool:
        headers = await async_req(url, method="HEAD", resp_type=Rt.HEADERS)
        size = headers.get("Content-Length", 0)
        if not size:
            logger.debug(f"HEAD {url} resp header has no Content-Length")
            return True
        ok = int(size) < 1024 * 1024 * 10
        if not ok:
            logger.warning(f"{url} size too large ({size * 1024:.2f} KB > 10240 KB)")
        return ok

    async def get_l2d(stu_name: str):
        if r := (await db_get_extra_l2d_list()).get(stu_name):
            return [f"{config.ba_bawiki_db_url}{x}" for x in r]

        cid = (await game_kee_get_stu_cid_li()).get(stu_name)
        if cid:
            l2d_list = await game_kee_grab_l2d(cid)
            checked_resp = await asyncio.gather(
                *(check_size(x) for x in l2d_list),
            )
            return [x for x, y in zip(l2d_list, checked_resp) if y]

        return None

    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        await matcher.finish("请提供学生名称或所需的羁绊等级")

    # 好感度等级
    if arg.isdigit():
        arg = int(arg)

        try:
            li = await get_fav_li(arg)
        except Exception:
            logger.exception("获取 SchaleDB 学生数据失败")
            await matcher.finish("获取 SchaleDB 学生数据失败，请检查后台输出")

        if not li:
            await matcher.finish(f"没有学生在羁绊等级{arg}时解锁L2D")

        try:
            p = await draw_fav_li(li)
        except Exception:
            logger.exception("绘制图片出错")
            await matcher.finish("绘制图片出错，请检查后台输出")

        await matcher.finish(
            f"羁绊等级 {arg} 时解锁L2D的学生有以下这些：" + MessageSegment.image(p),
        )

    # 学生名称
    arg = await recover_stu_alia(arg)

    try:
        ret = await schale_get_stu_dict()
    except Exception:
        logger.exception("获取学生列表出错")
        await matcher.finish("获取学生列表表出错，请检查后台输出")

    if stu := ret.get(arg):
        if not (lvl := stu["MemoryLobby"]):
            await matcher.finish("该学生没有L2D")

        try:
            pics = await get_l2d(await schale_to_gamekee(arg))
        except Exception:
            logger.exception("下载 L2D 图片出错")
            await matcher.finish("获取 L2D 图片列表出错，请检查后台输出")

        im = Message() + f'{stu["Name"]} 在羁绊等级 {lvl[0]} 时即可解锁L2D\n'
        if pics:
            try:
                images = await asyncio.gather(
                    *(async_req(x, resp_type=Rt.BYTES) for x in pics),
                )
            except Exception:
                logger.exception("下载 L2D 图片出错")
                await matcher.finish("下载 L2D 图片出错，请检查后台输出")
            image_seg = "L2D预览：" + Message(MessageSegment.image(x) for x in images)

        else:
            im += (
                "没找到该学生的L2D看板\n"
                "可能原因：\n"
                "- GameKee页面爬取不到角色L2D图片\n"
                "- GameKee和插件没有收录该学生的L2D\n"
            )
            await matcher.finish(im)

        try:
            await matcher.finish(im + image_seg)
        except ActionFailed as e:
            if image_seg:
                logger.warning(f"Failed to send message: ActionFailed: {e}")
                await matcher.finish(im + "抱歉，L2D 图片被风控了，或许是因为太涩了……")
            raise

    await matcher.finish("未找到学生")
