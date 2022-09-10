<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://raw.githubusercontent.com/lgc2333/nonebot-plugin-bawiki/master/readme/nonebot-plugin-bawiki.png" width="200" height="200" alt="BAWiki"></a>
</div>

<div align="center">

# NoneBot-Plugin-BAWiki

_✨ 基于 NoneBot2 的碧蓝档案 Wiki 插件 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/lgc2333/nonebot-plugin-bawiki.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-bawiki">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-bawiki.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
<a href="https://pypi.python.org/pypi/nonebot-plugin-bawiki">
    <img src="https://img.shields.io/pypi/dm/nonebot-plugin-bawiki" alt="pypi download">
</a>
<a href="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/371bbbba-9dba-4e40-883c-72b688876575">
    <img src="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/371bbbba-9dba-4e40-883c-72b688876575.svg" alt="wakatime">
</a>

</div>

## 💬 前言

诚邀各位帮忙扩充别名词库以及更新插件内置数据源！

本人在学校没有太多时间能够写代码，所以维护插件变成了一件比较困难的事  
感谢各位的帮助！

[点击跳转学生别名字典](https://github.com/lgc2333/nonebot-plugin-bawiki/blob/master/nonebot_plugin_bawiki/const.py#L1)  
[点击跳转学生 L2D 预览图列表](https://github.com/lgc2333/nonebot-plugin-bawiki/blob/master/nonebot_plugin_bawiki/const.py#L125)

修改后直接往本仓库提交 Pull Request 即可！

## 📖 介绍

一个碧蓝档案的 Wiki 插件，数据来源为 [GameKee](https://ba.gamekee.com/) 与 [SchaleDB](https://lonqie.github.io/SchaleDB/)  
插件灵感来源：[ba_calender](https://f.xiaolz.cn/forum.php?mod=viewthread&tid=145)

## 💿 安装

<details open>
<summary>【推荐】使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-bawiki

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-bawiki

</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-bawiki

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-bawiki

</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-bawiki

</details>

打开 nonebot2 项目的 `bot.py` 文件, 在其中写入

    nonebot.load_plugin('nonebot_plugin_bawiki')

</details>

<details>
<summary>从 github 安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 输入以下命令克隆此储存库

    git clone https://github.com/lgc2333/nonebot-plugin-bawiki.git

打开 nonebot2 项目的 `bot.py` 文件, 在其中写入

    nonebot.load_plugin('src.plugins.nonebot_plugin_bawiki')

</details>

## ⚙️ 配置

暂无

<!--
在 nonebot2 项目的`.env`文件中添加下表中的配置

| 配置项  | 必填 | 默认值 |            说明            |
| :-----: | :--: | :----: | :------------------------: |
| `proxy` |  否  | `None` | 访问`SchaleDB`时使用的代理 |
-->
## 🎉 使用

### 指令表

兼容 [nonebot-plugin-PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu)

![menu](https://raw.githubusercontent.com/lgc2333/nonebot-plugin-bawiki/master/readme/menu.png)

待更新

### 效果图

<details>
<summary>长图，点击展开</summary>

![example](https://raw.githubusercontent.com/lgc2333/nonebot-plugin-bawiki/master/readme/example.png)  
![example2](https://raw.githubusercontent.com/lgc2333/nonebot-plugin-bawiki/master/readme/example2.png)

</details>

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [RainNight0](https://github.com/RainNight0)

- 日程表 html 模板提供

### [黑枪灬王子](mailto:1109024495@qq.com)

- 学生别名提供

## 💰 赞助

感谢大家的赞助！你们的赞助将是我继续创作的动力！

- [爱发电](https://afdian.net/@lgc2333)
- <details>
    <summary>赞助二维码（点击展开）</summary>

  ![讨饭](https://raw.githubusercontent.com/lgc2333/ShigureBotMenu/master/src/imgs/sponsor.png)

  </details>

## 📝 更新日志

### 0.4.2

- `ba羁绊` `baL2D` 的 L2D 预览图改为实时从 GameKee 抓取

### 0.4.1

- 优化带括号学生名称的别名匹配

### 0.4.0

- `ba日程表`的`SchaleDB`数据源
- `ba学生图鉴` `ba羁绊` 数据源更换为`SchaleDB`
- 原`ba学生图鉴`修改为`ba学生wiki`

### 0.3.0

- 新指令 `baL2D`
- 新指令 `ba羁绊`

### 0.2.2

- 添加学生别名判断
- 修改日程表图片宽度

### 0.2.1

- 修改页面加载等待的事件，可能修复截图失败的问题

### 0.2.0

- 新指令 `ba新学生` （详情使用 [nonebot-plugin-PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu) 查看）

### 0.1.1

- 日程表改为以图片形式发送
- 日程表不会显示未开始的活动了
- 小 bug 修复
- ~~移除了 herobrine~~
