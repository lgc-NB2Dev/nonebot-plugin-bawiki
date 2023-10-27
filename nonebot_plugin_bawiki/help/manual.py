import re
from io import BytesIO
from typing import Dict, Tuple

from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from pil_utils import Text2Image

from ..command import help_list

usage = "使用指令 `ba帮助` 查询插件功能帮助"
extra = None

FT_REGEX = r"<ft(?P<args>.*?)>(?P<content>.*?)</ft>"


async def t2p(text: str) -> BytesIO:
    t2i = Text2Image.from_bbcode_text(text, fontsize=32)
    img = t2i.to_image("white", (16, 16)).convert("RGB")
    bio = BytesIO()
    img.save(bio, format="jpeg")
    bio.seek(0)
    return bio


async def t2pm(text: str) -> MessageSegment:
    bio = await t2p(text)
    return MessageSegment.image(bio)


def ft_args_to_bbcode(args: str) -> Tuple[str, str]:
    def parse_color(color: str) -> str:
        if color.startswith("(") and color.endswith(")"):
            hex_color = "".join(f"{int(x):02x}" for x in color[1:-1].split(","))
            return f"#{hex_color}"
        return color

    ft_args = dict(x.split("=") for x in args.strip().split())
    bbcode_args: Dict[str, str] = {}

    if "fonts" in ft_args:
        bbcode_args["font"] = ft_args["fonts"]
    if "size" in ft_args:
        bbcode_args["size"] = ft_args["size"]
    if "color" in ft_args:
        bbcode_args["color"] = parse_color(ft_args["color"])

    prefix = ""
    suffix = ""
    for k, v in bbcode_args.items():
        prefix = f"[{k}={v}]{prefix}"
        suffix = f"{suffix}[/{k}]"
    return prefix, suffix


def replace_ft(text: str) -> str:
    def replace(match: re.Match) -> str:
        args = match.group("args")
        prefix, suffix = ft_args_to_bbcode(args)
        content = match.group("content")
        return f"{prefix}{content}{suffix}"

    return re.sub(FT_REGEX, replace, text)


async def help_handle(matcher: Matcher, arg_msg: Message = CommandArg()):
    arg = arg_msg.extract_plain_text().strip()

    if not arg:
        cmd_list = "\n".join(
            (
                f"▸ [b]{k['func']}[/b] "
                f"({k['trigger_method']}：{k['trigger_condition']}) - "
                f"{k['brief_des']}"
            )
            for k in help_list
        )
        msg = (
            f"目前插件支持的功能：\n"
            f"\n"
            f"{cmd_list}\n"
            f"\n"
            f"Tip: 使用指令 `[b]ba帮助 <功能名>[/b]` 查看某功能详细信息"
        )
        await matcher.finish(await t2pm(msg))

    arg_lower = arg.lower()
    func = next(
        (
            x
            for x in help_list
            if (
                (arg_lower in x["func"].lower())
                or (arg_lower in x["trigger_condition"].lower())
                or (arg_lower in x["brief_des"].lower())
            )
        ),
        None,
    )
    if not func:
        await matcher.finish(f"未找到功能 `{arg}`")

    # ft to bbcode
    detail_des = replace_ft(func["detail_des"])

    # 缩进
    detail_des = "    ".join(detail_des.splitlines(keepends=True)).strip()

    msg = (
        f"▸ [b]功能：{func['func']}[/b]\n"
        f"\n"
        f'▹ [b]触发方式：[/b]{func["trigger_method"]}\n'
        f'▹ [b]触发条件：[/b]{func["trigger_condition"]}\n'
        f'▹ [b]简要描述：[/b]{func["brief_des"]}\n'
        f"▹ [b]详细描述：[/b]\n"
        f"    {detail_des}"
    )
    await matcher.finish(await t2pm(msg))
