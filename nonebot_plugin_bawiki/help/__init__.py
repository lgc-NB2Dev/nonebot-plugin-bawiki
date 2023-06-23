from nonebot import on_command

from ..command import help_list

try:
    from .pic_menu import extra as extra
    from .pic_menu import help_handle
    from .pic_menu import usage as usage
except ImportError:
    from .manual import extra as extra
    from .manual import help_handle
    from .manual import usage as usage


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
                "- <ft color=(238,120,0)>ba帮助</ft>\n"
                "- <ft color=(238,120,0)>ba菜单</ft>\n"
                "- <ft color=(238,120,0)>ba功能</ft>\n"
                " \n"
                "指令示例：\n"
                "- <ft color=(238,120,0)>ba帮助</ft>（功能列表）\n"
                "- <ft color=(238,120,0)>ba帮助 日程表</ft>（功能详情）"
            ),
        },
    )

    help_cmd = on_command("ba帮助", aliases={"ba菜单", "ba功能"})
    help_cmd.handle()(help_handle)
