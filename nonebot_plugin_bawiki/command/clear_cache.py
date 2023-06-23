from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.internal.matcher import Matcher
from nonebot.permission import SUPERUSER

from ..util import clear_req_cache

if TYPE_CHECKING:
    from . import HelpList

help_list: HelpList = [
    {
        "func": "清空缓存",
        "trigger_method": "超级用户 指令",
        "trigger_condition": "ba清空缓存",
        "brief_des": "清空插件请求缓存",
        "detail_des": (
            "手动清空插件请求网络缓存下来的数据（正常3小时清空一次）\n"
            "如果插件出问题了，或者你想提前看到新内容，不妨试试清空一下插件缓存\n"
            "注：该指令只能由<ft color=(238,120,0)>超级用户</ft>触发\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>ba清空缓存</ft>\n"
            "- <ft color=(238,120,0)>ba清除缓存</ft>"
        ),
    },
]


cmd_clear_cache = on_command("ba清空缓存", aliases={"ba清除缓存"}, permission=SUPERUSER)


@cmd_clear_cache.handle()
async def _(matcher: Matcher):
    clear_req_cache()
    await matcher.finish("缓存已清空～")
