<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="readme/nonebot-plugin-bawiki.png" width="200" height="200" alt="BAWiki"></a>
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

</div>

## 📖 介绍

一个碧蓝档案的 Wiki 插件，目前写了活动日程和学生图鉴，数据来源为 [GameKee](https://ba.gamekee.com/)

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

暂无配置

<!--
在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| 配置项1 | 是 | 无 | 配置说明 |
| 配置项2 | 否 | 无 | 配置说明 |
-->

## 🎉 使用

### 指令表

兼容 [nonebot-plugin-PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu)

|     指令     | 权限 | 需要@ | 范围 |                     说明                      |
| :----------: | :--: | :---: | :--: | :-------------------------------------------: |
|  `ba日程表`  |  无  |  否   | 均可 |                      无                       |
| `ba学生图鉴` |  无  |  否   | 均可 | 需要在后面加上学生名字，比如`ba学生图鉴 白子` |
|  `ba新学生`  |  无  |  否   | 均可 |                      无                       |

待更新

### 效果图

<details>
<summary>长图，点击展开</summary>

![example](readme/example.png)

</details>

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [RainNight0](https://github.com/RainNight0)

- 日程表 html 模板提供

## 💰 赞助

感谢大家的赞助！你们的赞助将是我继续创作的动力！

- [爱发电](https://afdian.net/@lgc2333)
- <details>
    <summary>赞助二维码（点击展开）</summary>

  ![讨饭](https://raw.githubusercontents.com/lgc2333/ShigureBotMenu/master/src/imgs/sponsor.png)

  </details>

## 📝 更新日志

### 0.2.1

- 修改页面加载等待的事件，可能修复截图失败的问题

### 0.2.0

- 新指令 `ba新学生` （详情使用 [nonebot-plugin-PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu) 查看）

### 0.1.1

- 日程表改为以图片形式发送
- 日程表不会显示未开始的活动了
- 小 bug 修复
- ~~移除了 herobrine~~
