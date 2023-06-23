import re

from nonebot.internal.adapter import Message
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg

from ..command import help_list

usage = "使用指令 `ba帮助` 查询插件功能帮助"
extra = None

FT_START_REGEX = r"<ft color=\((\d+),(\d+),(\d+)\)>"
FT_END_REGEX = r"</ft>"


async def help_handle(matcher: Matcher, arg_msg: Message = CommandArg()):
    arg = arg_msg.extract_plain_text().strip()

    if not arg:
        cmd_list = "\n".join(f"▶ {k}" for k in [x["func"] for x in help_list])
        await matcher.finish(
            f"目前插件支持的功能：\n"
            f"\n"
            f"{cmd_list}\n"
            f"\n"
            f"Tip: 使用指令 `ba帮助 <功能名>` 查看某功能详细信息",
        )

    func = next((x for x in help_list if arg in x["func"]), None)
    if not func:
        await matcher.finish(f"未找到功能 `{arg}`")

    # 去掉 <ft> 富文本标签
    detail_des = re.sub(FT_START_REGEX, "", func["detail_des"])
    detail_des = re.sub(FT_END_REGEX, "", detail_des)

    # 缩进
    detail_des = "    ".join(detail_des.splitlines(keepends=True)).strip()

    await matcher.finish(
        f"▶ 功能：{func['func']}\n"
        f"\n"
        f'▷ 触发方式：{func["trigger_method"]}\n'
        f'▷ 触发条件：{func["trigger_condition"]}\n'
        f'▷ 简要描述：{func["brief_des"]}\n'
        f"▷ 详细描述：\n"
        f"    {detail_des}",
    )
