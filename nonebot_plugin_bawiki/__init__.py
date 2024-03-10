from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")

from .command import load_commands  # noqa: E402
from .config import Cfg as Cfg  # noqa: E402
from .help import extra, register_help_cmd, usage  # noqa: E402

__version__ = "0.11.2"
__plugin_meta__ = PluginMetadata(
    name="BAWiki",
    description="碧蓝档案Wiki插件",
    usage=usage,
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki",
    type="application",
    config=Cfg,
    supported_adapters={"~onebot.v11"},
    extra={"License": "MIT", "Author": "student_2333"},
)

if extra:
    __plugin_meta__.extra.update(extra)

register_help_cmd()
load_commands()
