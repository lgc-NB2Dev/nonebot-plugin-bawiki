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

诚邀各位帮忙更新插件数据源仓库！能帮这个小小插件贡献微薄之力，鄙人感激不尽！！

[点击跳转 bawiki-data](https://github.com/lgc2333/bawiki-data)

修改后提交 Pull Request 即可！

## 📖 介绍

一个碧蓝档案的 Wiki 插件，主要数据来源为 [GameKee](https://ba.gamekee.com/) 与 [SchaleDB](https://lonqie.github.io/SchaleDB/)  
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

在 nonebot2 项目的`.env`文件中添加下表中的配置

| 配置项  | 必填 | 默认值 |                         说明                          |
| :-----: | :--: | :----: | :---------------------------------------------------: |
| `PROXY` |  否  | `None` | 访问`SchaleDB`、`bawiki-data`的 json 数据时使用的代理 |

## 🎉 使用

### 指令表

兼容 [nonebot-plugin-PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu)

见[这里](https://github.com/lgc2333/nonebot-plugin-bawiki/blob/master/nonebot_plugin_bawiki/__init__.py#L17)

待更新

<!--
### 效果图

<details>
<summary>长图，点击展开</summary>

![example](https://raw.githubusercontent.com/lgc2333/nonebot-plugin-bawiki/master/readme/example.png)
![example2](https://raw.githubusercontent.com/lgc2333/nonebot-plugin-bawiki/master/readme/example2.png)

</details>
-->

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [RainNight0](https://github.com/RainNight0)

- 日程表 html 模板提供（已弃用）

### `bawiki-data`数据源贡献列表

- 见 [bawiki-data](http://github.com/lgc2333/bawiki-data)

## 💰 赞助

感谢大家的赞助！你们的赞助将是我继续创作的动力！

- [爱发电](https://afdian.net/@lgc2333)
- <details>
    <summary>赞助二维码（点击展开）</summary>

  ![讨饭](https://raw.githubusercontent.com/lgc2333/ShigureBotMenu/master/src/imgs/sponsor.png)

  </details>

## 📝 更新日志

### 0.6.4

- 修复由于 `imageutils` 接口改动造成的绘图失败的 bug

### 0.6.3

- 使用 `require` 加载依赖插件

### 0.6.2

- 修改日程表、羁绊查询的图片背景
- 加上日程表条目的圆角
- 更改 GameKee 日程表的排序方式

### 0.6.1

- 修复一处 Py 3.8 无法运行的代码

### 0.6.0

- 新指令 `ba抽卡` `ba切换卡池` `ba表情` `ba漫画`
- 更改 SchaleDB 日程表触发单国际服的指令判断（由包含`国际服`改为包含`国`）

### 0.5.2

- 新指令`ba语音`
- 修复`ba综合战术考试`的一些问题

### 0.5.1

- 新指令`ba互动家具`
- `ba国际服千里眼`指令的日期参数如果小于当前日期则会将日期向前推一年
- `ba日程表`的 SchaleDB 源如果没获取到数据则不会绘画那一部分
- `ba国际服千里眼`日期匹配 bug 修复

### 0.5.0

- 新数据源 [bawiki-data](http://github.com/lgc2333/bawiki-data)
- 新指令`ba角评`；`ba总力战`；`ba活动`；`ba综合战术考试`；`ba制造`；`ba国际服千里眼`；`ba清空缓存`
- 将`bal2d`指令改为`ba羁绊`别名
- 将`ba日程表`指令从网页截图改为 Pillow 画图；并修改了指令的参数解析方式
- 更改了`ba羁绊`指令的画图方式及底图
- 更改学生别名的匹配方式
- 学生别名等常量现在从 [bawiki-data](http://github.com/lgc2333/bawiki-data) 在线获取
- 新增请求接口的缓存机制，每3小时清空一次缓存
- 新增`PROXY`配置项
- 更改三级菜单排版

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
