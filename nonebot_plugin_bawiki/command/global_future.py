import datetime
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg

from ..data.bawiki import db_global_future

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "国际服千里眼",
        "trigger_method": "指令",
        "trigger_condition": "ba千里眼",
        "brief_des": "查询国际服未来的卡池与活动",
        "detail_des": (
            "发送当前或指定日期的国际服未来卡池与活动列表\n"
            "图片作者 B站@夜猫咪喵喵猫\n"
            " \n"
            "参数可以指定起始日期以及列表个数，但同时指定时请将日期放在列表个数前面，以空格分隔\n"
            "参数中含有`全`或`a`时会发送整张前瞻图\n"
            " \n"
            "日期格式可以为（Y代表4位数年，m代表月，d代表日）：\n"
            "- <ft color=(238,120,0)>Y/m/d</ft>；<ft color=(238,120,0)>m/d</ft>\n"
            "- <ft color=(238,120,0)>Y-m-d</ft>；<ft color=(238,120,0)>m-d</ft>\n"
            "- <ft color=(238,120,0)>Y年m月d日</ft>；<ft color=(238,120,0)>m月d日</ft>\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>ba国际服千里眼</ft>\n"
            "- <ft color=(238,120,0)>ba千里眼</ft>\n"
            "- <ft color=(238,120,0)>ba国际服前瞻</ft>\n"
            "- <ft color=(238,120,0)>ba前瞻</ft>\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba千里眼</ft>\n"
            "- <ft color=(238,120,0)>ba千里眼 all</ft>\n"
            "- <ft color=(238,120,0)>ba千里眼 3</ft>\n"
            "- <ft color=(238,120,0)>ba千里眼 11/15</ft>\n"
            "- <ft color=(238,120,0)>ba千里眼 11/15 3</ft>"
        ),
    },
]


cmd_global_future = on_command("ba国际服千里眼", aliases={"ba千里眼", "ba国际服前瞻", "ba前瞻"})


@cmd_global_future.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if "全" in args or "a" in args:
        await matcher.finish(await db_global_future(all_img=True))

    args = args.split()
    num = 1
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
            try:
                parsed_date = datetime.datetime.strptime(date.replace(" ", ""), f)
                break
            except ValueError:
                pass
        if not parsed_date:
            await matcher.finish("日期格式不正确！")
        date = parsed_date
        if date.year == 1900:
            now = datetime.datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            date = date.replace(year=now.year)
            if date < now:
                date = date.replace(year=now.year + 1)

    if isinstance(num, str) and ((not num.isdigit()) or (num := int(num)) < 1):
        await matcher.finish("前瞻项目数量格式不正确！")

    await matcher.finish(await db_global_future(date or None, num))
