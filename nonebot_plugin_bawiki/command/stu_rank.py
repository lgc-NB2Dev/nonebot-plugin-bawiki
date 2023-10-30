from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..data.bawiki import db_wiki_stu, recover_stu_alia
from ..help import FT_E, FT_S

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "学生评价",
        "trigger_method": "指令",
        "trigger_condition": "ba角评",
        "brief_des": "查询学生角评一图流",
        "detail_des": (
            "发送一张指定角色的评价图\n"
            "支持部分学生别名\n"
            "角评图作者 B站@夜猫咪喵喵猫\n"
            " \n"
            "可以使用 `all` / `总览` / `全部` 参数 查看全学生角评一图流\n"
            " \n"
            "可以用这些指令触发：\n"
            f"- {FT_S}ba学生评价{FT_E}\n"
            f"- {FT_S}ba角评{FT_E}\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba学生评价 白子{FT_E}\n"
            f"- {FT_S}ba角评 xcw{FT_E}\n"
            f"- {FT_S}ba角评 总览{FT_E}"
        ),
    },
]


cmd_stu_rank = on_command("ba学生评价", aliases={"ba角评"})


@cmd_stu_rank.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        await matcher.finish("请提供学生名称")

    if arg == "总览" or arg == "全部" or arg.lower() == "all":
        arg = "all"
    else:
        arg = await recover_stu_alia(arg)

    try:
        im = await db_wiki_stu(arg)
    except Exception:
        logger.exception("获取角评出错")
        await matcher.finish("获取角评出错，请检查后台输出")

    await matcher.finish(im)
