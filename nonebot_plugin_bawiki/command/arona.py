from typing import TYPE_CHECKING, List, NoReturn

from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.typing import T_State

from ..data.arona import ImageModel, get_image, search

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "Arona数据源攻略",
        "trigger_method": "指令",
        "trigger_condition": "arona",
        "brief_des": "从Arona Bot数据源中搜索攻略图",
        "detail_des": (
            "从Arona Bot数据源中搜索攻略图，支持模糊搜索\n"
            " \n"
            "可以搜索的内容：\n"
            "- <ft color=(238,120,0)>学生攻略图</ft>（星野，白子 等）\n"
            "- <ft color=(238,120,0)>主线地图</ft>（1-1，H1-1 等）\n"
            "- <ft color=(238,120,0)>杂图</ft>（使用 <ft color=(238,120,0)>arona 杂图</ft> 可以获取图片列表）\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>arona</ft>\n"
            "- <ft color=(238,120,0)>Arona</ft>\n"
            "- <ft color=(238,120,0)>ARONA</ft>\n"
            "- <ft color=(238,120,0)>阿罗娜</ft>\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>arona</ft>（会向你提问需要搜索什么）\n"
            "- <ft color=(238,120,0)>arona 国际服未来视</ft>（精确搜索）\n"
            "- <ft color=(238,120,0)>arona 国际服</ft>（模糊搜索）"
        ),
    },
]


cmd_arona = on_command("arona", aliases={"Arona", "ARONA", "阿罗娜"})


async def send_image(matcher: Matcher, img: ImageModel) -> NoReturn:
    try:
        res = await get_image(img.path, img.hash)
    except Exception:
        logger.exception("Arona数据源图片获取失败")
        await matcher.finish("图片获取失败，请稍后再试")

    await matcher.finish(MessageSegment.image(res))


@cmd_arona.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    if arg.extract_plain_text().strip():
        matcher.set_arg("param", arg)


@cmd_arona.got("param", prompt="请输入要搜索的关键词")
async def _(matcher: Matcher, state: T_State, param: str = ArgPlainText()):
    param = param.strip()
    if not param:
        await matcher.reject("关键词不能为空，请重新输入")

    try:
        res = await search(param)
    except Exception:
        logger.exception("Arona数据源搜索失败")
        await matcher.finish("搜索失败，请稍后再试")

    if not res:
        await matcher.finish("没有找到相关图片")

    if len(res) == 1:
        await send_image(matcher, res[0])

    state["res"] = res
    await matcher.pause(
        "Arona 查到了多个结果，请 sensei 发送序号选择~\n"
        + "\n".join(f"{i}. {r.name}" for i, r in enumerate(res, 1))
        + "\nTip：发送 0 取消选择",
    )


@cmd_arona.handle()
async def _(event: MessageEvent, matcher: Matcher, state: T_State):
    index_str = event.get_plaintext().strip()
    res: List[ImageModel] = state["res"]

    if not (index_str.isdigit() and (0 <= (index := int(index_str)) <= len(res))):
        await matcher.reject("序号错误，请重新输入")

    if index == 0:
        await matcher.finish("操作已取消")

    param = res[index - 1].name
    try:
        final_res = await search(param)
        assert final_res
    except Exception:
        logger.exception("Arona数据源搜索失败")
        await matcher.finish("搜索失败，请稍后再试")

    await send_image(matcher, final_res[0])
