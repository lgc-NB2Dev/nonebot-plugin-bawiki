import json
from io import BytesIO
from pathlib import Path
from typing import Union, cast

from nonebot import get_available_plugin_names, logger, require
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.internal.adapter import Message
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from PIL import Image
from pil_utils.fonts import get_proper_font

from ..command import help_list
from .const import FT_E, FT_S

# import importlib.util
# if importlib.util.find_spec("nonebot_plugin_PicMenu") is None:

if "nonebot_plugin_PicMenu" not in get_available_plugin_names():
    raise ImportError

require("nonebot_plugin_PicMenu")

from nonebot_plugin_PicMenu import menu_manager  # noqa: E402

usage = f"请使用指令 [ba帮助 {FT_S}功能名称或序号{FT_E}] 查看某功能详细介绍"
extra = {"menu_template": "default", "menu_data": help_list}


def save_img_to_io(img: Image.Image):
    img = img.convert("RGB")
    img_io = BytesIO()
    img.save(img_io, "jpeg")
    img_io.seek(0)
    return img_io


async def help_handle(matcher: Matcher, arg_msg: Message = CommandArg()):
    arg = arg_msg.extract_plain_text().strip()
    img = cast(
        Union[str, Image.Image],
        (
            menu_manager.generate_plugin_menu_image("BAWiki")
            if not arg
            else menu_manager.generate_func_details_image("BAWiki", arg)
        ),
    )

    if isinstance(img, str):
        await matcher.finish(f'出错了，可能未找到功能 "{arg}"')

    await matcher.finish(MessageSegment.image(save_img_to_io(img)))


# 给 PicMenu 用户上个默认字体
def set_pic_menu_font():
    pic_menu_dir = Path.cwd() / "menu_config"
    pic_menu_config = pic_menu_dir / "config.json"

    if not pic_menu_dir.exists():
        pic_menu_dir.mkdir(parents=True)

    if (not pic_menu_config.exists()) or (
        json.loads(pic_menu_config.read_text(encoding="u8")).get("default")
        == "font_path"
    ):
        path = str(get_proper_font("国").path.resolve())
        pic_menu_config.write_text(json.dumps({"default": path}), encoding="u8")
        logger.info("检测到 PicMenu 已加载并且未配置字体，已自动帮您配置系统字体")


try:
    set_pic_menu_font()
except Exception:
    logger.exception("配置 PicMenu 字体失败")
