from typing import TYPE_CHECKING, List, NoReturn

from nonebot import logger, on_command, on_shell_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg, ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.rule import ArgumentParser, Namespace
from nonebot.typing import T_State

from ..config import config
from ..data.arona import ImageModel, get_image, search, search_exact, set_alias
from ..help import FT_E, FT_S
from ..util import IllegalOperationFinisher

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "Arona数据源攻略",
        "trigger_method": "指令",
        "trigger_condition": "arona",
        "brief_des": "从 Arona Bot 数据源中搜索攻略图",
        "detail_des": (
            "从 Arona Bot 数据源中搜索攻略图，支持模糊搜索\n"
            "感谢 diyigemt 佬的开放 API 数据源\n"
            " \n"
            f"可以使用 {FT_S}arona设置别名{FT_E} 指令来为某关键词设置别名\n"
            f"使用方式：{FT_S}arona设置别名 原名 别名1 别名2 ...{FT_E}\n"
            "\n"
            f"可以使用 {FT_S}arona删除别名{FT_E} 指令来删除已设置的关键词的别名\n"
            f"使用方式：{FT_S}arona删除别名 别名1 别名2 ...{FT_E}\n"
            " \n"
            "可以搜索的内容：\n"
            f"- {FT_S}学生攻略图{FT_E}（星野，白子 等）\n"
            f"- {FT_S}主线地图{FT_E}（1-1，H1-1 等）\n"
            f"- {FT_S}杂图{FT_E}（使用 {FT_S}arona 杂图{FT_E} 可以获取图片列表）\n"
            " \n"
            "可以用这些指令触发：\n"
            f"- {FT_S}arona{FT_E}\n"
            f"- {FT_S}蓝色恶魔{FT_E}\n"
            f"- {FT_S}Arona{FT_E}\n"
            f"- {FT_S}ARONA{FT_E}\n"
            f"- {FT_S}阿罗娜{FT_E}\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}arona{FT_E}（会向你提问需要搜索什么）\n"
            f"- {FT_S}arona 国际服未来视{FT_E}（精确搜索）\n"
            f"- {FT_S}arona 国际服{FT_E}（模糊搜索）"
        ),
    },
]


illegal_finisher = IllegalOperationFinisher("坏老师，一直逗我，不理你了，哼！")

ARONA_PREFIXES = ["arona", "蓝色恶魔", "Arona", "ARONA", "阿罗娜"]
cmd_arona = on_command(ARONA_PREFIXES[0], aliases=set(ARONA_PREFIXES[1:]), priority=2)


async def send_image(matcher: Matcher, img: ImageModel) -> NoReturn:
    try:
        res = await get_image(img.path, img.hash)
    except Exception:
        logger.exception("Arona数据源图片获取失败")
        await matcher.finish("呜呜，阿罗娜在获取图片的时候遇到了点问题 QAQ")

    await matcher.finish(MessageSegment.image(res))


@cmd_arona.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        matcher.set_arg("param", arg)


@cmd_arona.got("param", prompt="老师，请发送想要搜索的内容~")
async def _(matcher: Matcher, state: T_State, param: str = ArgPlainText()):
    param = param.strip()
    if not param:
        await illegal_finisher()
        await matcher.reject("老师真是的，快给我发送你想要搜索的内容吧！")

    try:
        res = await search(param)
    except Exception:
        logger.exception("Arona数据源搜索失败")
        await matcher.finish("呜呜，阿罗娜在搜索结果的时候遇到了点问题 QAQ")

    if not res:
        await matcher.finish("抱歉老师，阿罗娜没有找到相关结果……")

    if len(res) == 1:
        await send_image(matcher, res[0])

    state["res"] = res
    list_txt = "\n".join(f"{i}. {r.name}" for i, r in enumerate(res, 1))
    await matcher.pause(
        f"老师！阿罗娜帮您找到了多个可能的结果，请发送序号来选择吧~\n{list_txt}\nTip：发送 0 取消选择",
    )


@cmd_arona.handle()
async def _(event: MessageEvent, matcher: Matcher, state: T_State):
    index_str = event.get_plaintext().strip()
    res: List[ImageModel] = state["res"]

    if index_str == "0":
        await matcher.finish("OK，阿罗娜已经取消老师的选择了~")

    if not index_str.isdigit():
        await illegal_finisher()
        await matcher.reject("不要再逗我了，老师！快发送你要选择的序号吧 quq")

    index = int(index_str)
    if not (0 <= index <= len(res)):
        await illegal_finisher()
        await matcher.reject("抱歉，阿罗娜找不到老师发送的序号哦，请老师重新发送一下吧")

    param = res[index - 1].name
    try:
        final_res = await search(param)
        assert final_res
    except Exception:
        logger.exception("Arona数据源搜索失败")
        await matcher.finish("呜呜，阿罗娜在搜索结果的时候遇到了点问题 QAQ")

    await send_image(matcher, final_res[0])


ARONA_SET_ALIAS_COMMANDS = [f"{p}设置别名" for p in ARONA_PREFIXES]
ARONA_DEL_ALIAS_COMMANDS = [f"{p}删除别名" for p in ARONA_PREFIXES]

cmd_arona_set_alias_parser = ArgumentParser(ARONA_SET_ALIAS_COMMANDS[0])
cmd_arona_set_alias_parser.add_argument("name", help="原名")
cmd_arona_set_alias_parser.add_argument("aliases", nargs="+", help="别名，可以提供多个")
cmd_arona_set_alias = on_shell_command(
    ARONA_SET_ALIAS_COMMANDS[0],
    aliases=set(ARONA_SET_ALIAS_COMMANDS[1:]),
    parser=cmd_arona_set_alias_parser,
    permission=SUPERUSER if config.ba_arona_set_alias_only_su else None,
)

cmd_aro_del_alias_parser = ArgumentParser(ARONA_DEL_ALIAS_COMMANDS[0])
cmd_aro_del_alias_parser.add_argument("aliases", nargs="+", help="别名，可以提供多个")
cmd_arona_del_alias = on_shell_command(
    ARONA_DEL_ALIAS_COMMANDS[0],
    aliases=set(ARONA_DEL_ALIAS_COMMANDS[1:]),
    parser=cmd_aro_del_alias_parser,
    permission=SUPERUSER if config.ba_arona_set_alias_only_su else None,
)


@cmd_arona_set_alias.handle()
@cmd_arona_del_alias.handle()
async def _(matcher: Matcher, foo: ParserExit = ShellCommandArgs()):
    await matcher.finish(foo.message)


@cmd_arona_set_alias.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    try:
        assert isinstance(args.name, str)
        assert all(isinstance(a, str) for a in args.aliases)
    except AssertionError:
        await matcher.finish("请老师发送纯文本消息的说")

    name: str = args.name.strip()
    aliases: List[str] = [a.strip().lower() for a in args.aliases]

    try:
        resp = await search_exact(name)
    except Exception:
        logger.exception(f"Arona数据源搜索失败 {args.name}")
        await matcher.finish("抱歉，阿罗娜在尝试查找原名是否存在时遇到了一点小问题……")

    if (not resp) or (len(resp) > 1):
        await matcher.finish(
            "啊咧？阿罗娜找不到老师提供的原名，请老师检查一下您提供的名称是否正确",
        )

    ret_dict = set_alias(name, aliases)
    message = "\n".join(
        (
            "好的，阿罗娜已经成功帮你操作了以下别名~",
            *(
                (
                    f"成功将别名 {k} 指向的原名从 {v} 更改为 {name}"
                    if v
                    else f"成功设置 {k} 为 {name} 的别名"
                )
                for k, v in ret_dict.items()
            ),
        ),
    )
    await matcher.finish(message)


@cmd_arona_del_alias.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    try:
        assert all(isinstance(a, str) for a in args.aliases)
    except AssertionError:
        await matcher.finish("请老师发送纯文本消息的说")

    aliases: List[str] = [a.strip().lower() for a in args.aliases]

    ret_dict = set_alias(None, aliases)
    message = "\n".join(
        (
            "好的，阿罗娜已经成功帮你操作了以下别名~",
            *(
                (
                    f"成功删除指向原名 {v} 的别名 {k} "
                    if v
                    else f"已设置的别名中未找到 {k}"
                )
                for k, v in ret_dict.items()
            ),
        ),
    )
    await matcher.finish(message)
