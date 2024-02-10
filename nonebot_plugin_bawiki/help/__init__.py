from nonebot import on_command

from ..command import help_list
from .const import FT_E as FT_E, FT_S as FT_S

try:
    from .pic_menu import extra as extra, help_handle, usage as usage
except ImportError:
    from .manual import extra as extra, help_handle, usage as usage


def register_help_cmd():
    help_list.append(
        {
            "func": "插件帮助",
            "trigger_method": "指令",
            "trigger_condition": "ba帮助",
            "brief_des": "查看插件功能帮助",
            "detail_des": (
                "查看插件的功能列表，或某功能的详细介绍\n"
                "装载 PicMenu 插件后插件将会调用 PicMenu 生成帮助图片\n"
                " \n"
                "可以用这些指令触发：\n"
                f"- {FT_S}ba帮助{FT_E}\n"
                f"- {FT_S}ba菜单{FT_E}\n"
                f"- {FT_S}ba功能{FT_E}\n"
                " \n"
                "指令示例：\n"
                f"- {FT_S}ba帮助{FT_E}（功能列表）\n"
                f"- {FT_S}ba帮助 日程表{FT_E}（功能详情）"
            ),
        },
    )

    help_cmd = on_command("ba帮助", aliases={"ba菜单", "ba功能"})
    help_cmd.handle()(help_handle)
