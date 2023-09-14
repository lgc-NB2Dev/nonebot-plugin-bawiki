from typing import TYPE_CHECKING, List, NoReturn

from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.typing import T_State

from ..data.arona import ImageModel, get_image, search
from ..help import FT_E, FT_S

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "Arona数据源攻略",
        "trigger_method": "指令",
        "trigger_condition": "arona",
        "brief_des": "从 Arona Bot 数据源中搜索攻略图",
        "detail_des": (
            "从Arona Bot数据源中搜索攻略图，支持模糊搜索\n"
            "感谢 diyigemt 佬的开放 API 数据源\n"
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


cmd_arona = on_command("arona", aliases={"蓝色恶魔", "Arona", "ARONA", "阿罗娜"})


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
        f"阿罗娜找到了多个可能的结果，请老师发送序号来选择吧~\n{list_txt}\nTip：发送 0 取消选择",
    )


@cmd_arona.handle()
async def _(event: MessageEvent, matcher: Matcher, state: T_State):
    index_str = event.get_plaintext().strip()
    res: List[ImageModel] = state["res"]

    if index_str == "0":
        await matcher.finish("OK，阿罗娜已经取消老师的选择了~")

    if not index_str.isdigit():
        await matcher.reject("不要再逗我了，老师！快发送你要选择的序号吧quq")
    index = int(index_str)
    if not (0 <= index <= len(res)):
        await matcher.reject("阿罗娜找不到老师发送的序号哦，请老师重新发送一下吧")

    param = res[index - 1].name
    try:
        final_res = await search(param)
        assert final_res
    except Exception:
        logger.exception("Arona数据源搜索失败")
        await matcher.finish("呜呜，阿罗娜在搜索结果的时候遇到了点问题 QAQ")

    await send_image(matcher, final_res[0])
