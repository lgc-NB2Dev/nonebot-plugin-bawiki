import datetime
from contextlib import suppress
from typing import TYPE_CHECKING, Literal, Optional

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State

from ..data.bawiki import db_future
from ..help import FT_E, FT_S

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "更新前瞻",
        "trigger_method": "指令",
        "trigger_condition": "ba千里眼",
        "brief_des": "查询国际服/国服未来的卡池与活动",
        "detail_des": (
            "发送当前或指定日期的国际服/国服未来卡池与活动列表\n"
            "图片作者 B站@夜猫咪喵喵猫\n"
            " \n"
            "参数可以指定起始日期以及列表个数，但同时指定时请将日期放在列表个数前面，以空格分隔\n"
            "参数中含有 `全` 或 `a` 时会发送整张前瞻图\n"
            " \n"
            "参数以 `国际服` 或 `国际` 或 `global` 或 `g` 开头时会发送 国际服 前瞻图\n"
            "参数以 `国服` 或 `国` 或 `chinese` 或 `c` 开头时会发送 国服 前瞻图\n"
            "如果参数不以这些词开头时，默认发送国际服前瞻图\n"
            " \n"
            "日期格式可以为（Y代表4位数年，m代表月，d代表日）：\n"
            f"- {FT_S}Y/m/d{FT_E}；{FT_S}m/d{FT_E}\n"
            f"- {FT_S}Y-m-d{FT_E}；{FT_S}m-d{FT_E}\n"
            f"- {FT_S}Y年m月d日{FT_E}；{FT_S}m月d日{FT_E}\n"
            " \n"
            "可以用这些指令触发：\n"
            f"- {FT_S}ba千里眼{FT_E}\n"
            f"- {FT_S}ba前瞻{FT_E}\n"
            " \n"
            "有以下指令别名：\n"
            f"- {FT_S}ba国服千里眼{FT_E} 或 {FT_S}ba国服前瞻{FT_E} -> {FT_S}ba千里眼 国服{FT_E}\n"
            f"- {FT_S}ba国际服千里眼{FT_E} 或 {FT_S}ba国际服前瞻{FT_E} -> {FT_S}ba千里眼 国际服{FT_E}\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba千里眼{FT_E}\n"
            f"- {FT_S}ba千里眼 all{FT_E}\n"
            f"- {FT_S}ba千里眼 3{FT_E}\n"
            f"- {FT_S}ba千里眼 11/15{FT_E}\n"
            f"- {FT_S}ba千里眼 11/15 3{FT_E}\n"
            f"- {FT_S}ba千里眼 国服{FT_E}\n"
            f"- {FT_S}ba千里眼 国际服 11/15{FT_E}"
        ),
    },
]


GLOBAL_PFX = ("国际服", "国际", "global", "g")
CHINESE_PFX = ("国服", "国", "chinese", "c")

cmd_future = on_command("ba千里眼", aliases={"ba前瞻"})
cmd_global_future = on_command(
    "ba国际服千里眼",
    aliases={"ba国际服前瞻"},
    state={"future_type": "global"},
)
cmd_chinese_future = on_command(
    "ba国服千里眼",
    aliases={"ba国服前瞻"},
    state={"future_type": "chinese"},
)


@cmd_future.handle()
@cmd_global_future.handle()
@cmd_chinese_future.handle()
async def _(matcher: Matcher, state: T_State, arg: Message = CommandArg()):
    args = arg.extract_plain_text().lower().strip()

    future_type: Optional[Literal["global", "chinese"]] = state.get("future_type")
    if not future_type:
        used_global_pfx = next(filter(args.startswith, GLOBAL_PFX), None)
        used_chinese_pfx = next(filter(args.startswith, CHINESE_PFX), None)

        used_pfx = next((x for x in (used_chinese_pfx, used_global_pfx) if x), None)
        if used_pfx:
            args = args[len(used_pfx) :].strip()

        is_chinese = used_chinese_pfx
        future_type = "chinese" if is_chinese else "global"

    if "全" in args or "a" in args:
        await matcher.finish(await db_future(future_type, all_img=True))

    args = args.split()
    num = 3
    date = None
    if (args_len := len(args)) == 1:
        if args[0].isdigit():
            num = args[0]
        else:
            date = args[0]
    elif args_len > 1:
        date = args[0].strip()
        num = args[-1].strip()

    if date:
        parsed_date = None
        for f in ["%Y/%m/%d", "%Y-%m-%d", "%Y年%m月%d日", "%m/%d", "%m-%d", "%m月%d日"]:
            with suppress(ValueError):
                parsed_date = datetime.datetime.strptime(
                    date.replace(" ", ""),
                    f,
                ).astimezone()
                break
        if not parsed_date:
            await matcher.finish("日期格式不正确！")
        date = parsed_date
        if date.year == 1900:
            now = (
                datetime.datetime.now()
                .astimezone()
                .replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
            )
            date = date.replace(year=now.year)
            if date < now:
                date = date.replace(year=now.year + 1)

    if isinstance(num, str) and ((not num.isdigit()) or (num := int(num)) < 1):
        await matcher.finish("前瞻项目数量格式不正确！")

    await matcher.finish(await db_future(future_type, date or None, num))
