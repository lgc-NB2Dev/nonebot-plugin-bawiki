from pathlib import Path
from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.internal.matcher import Matcher
from nonebot.permission import SUPERUSER

from ..resource import CACHE_PATH
from ..util import clear_req_cache

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "清空缓存",
        "trigger_method": "超级用户 指令",
        "trigger_condition": "ba清空缓存",
        "brief_des": "清空插件请求缓存",
        "detail_des": (
            "手动清空插件请求网络缓存下来的数据，如API返回的数据\n"
            "注：该指令只能由<ft color=(238,120,0)>超级用户</ft>触发\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>ba清空缓存</ft>\n"
            "- <ft color=(238,120,0)>ba清除缓存</ft>"
        ),
    },
]


def clear_cache_dir() -> int:
    counter = 0

    def run(path: Path):
        nonlocal counter
        for p in path.iterdir():
            if p.is_dir():
                run(p)
            else:
                p.unlink()
                counter += 1

    run(CACHE_PATH)
    return counter


cmd_clear_cache = on_command("ba清空缓存", aliases={"ba清除缓存"}, permission=SUPERUSER)


@cmd_clear_cache.handle()
async def _(matcher: Matcher):
    req_count = clear_req_cache()
    cache_count = clear_cache_dir()
    await matcher.finish(f"已清除 {req_count} 项请求缓存与 {cache_count} 项文件缓存～")
