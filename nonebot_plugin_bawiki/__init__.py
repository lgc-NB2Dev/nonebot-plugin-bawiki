from nonebot.plugin import PluginMetadata

from .__main__ import *  # type:ignore

__version__ = "0.2.1"
__plugin_meta__ = PluginMetadata(
    name="BAWiki",
    description="碧蓝档案Wiki插件",
    usage="",
    extra={
        "menu_data": [
            {
                "func": "日程表",
                "trigger_method": "指令",
                "trigger_condition": "ba日程表",
                "brief_des": "查看活动日程表",
                "detail_des": "查看当前未结束的卡池、活动以及起止时间",
            },
            {
                "func": "学生图鉴",
                "trigger_method": "指令",
                "trigger_condition": "ba学生图鉴",
                "brief_des": "查询学生详情",
                "detail_des": "访问对应学生Wiki页面并截图\n"
                "指令示例：<ft color=(238,120,0)>ba学生图鉴 白子</ft>",
            },
            {
                "func": "新学生导航",
                "trigger_method": "指令",
                "trigger_condition": "ba新学生",
                "brief_des": "快速查询当期UP学生",
                "detail_des": "快速查询各日服、国际服当前UP学生简介与国际服下期预测UP",
            },
        ],
        "menu_template": "default",
    },
)
