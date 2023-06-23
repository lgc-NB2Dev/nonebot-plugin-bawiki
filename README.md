<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/bawiki/nonebot-plugin-bawiki.png" width="200" height="200" alt="BAWiki"></a>
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

[点击跳转 bawiki-data 查看详细贡献说明](https://github.com/lgc2333/bawiki-data)

## 📖 介绍

一个碧蓝档案的 Wiki 插件，主要数据来源为 [GameKee](https://ba.gamekee.com/) 与 [SchaleDB](https://lonqie.github.io/SchaleDB/)  
插件灵感来源：[ba_calender](https://f.xiaolz.cn/forum.php?mod=viewthread&tid=145)

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-bawiki
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-bawiki
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-bawiki
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-bawiki
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-bawiki
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_bawiki"
]
```

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的配置

|            配置项             | 必填 | 默认值  |                           说明                            |
| :---------------------------: | :--: | :-----: | :-------------------------------------------------------: |
|          `BA_PROXY`           |  否  | `None`  |  访问 `SchaleDB`、`bawiki-data` 的 json 数据时使用的代理  |
|     `BA_GACHA_COOL_DOWN`      |  否  |   `0`   |                每群每人的抽卡冷却，单位秒                 |
|      `BA_VOICE_USE_CARD`      |  否  | `False` |            是否使用自定义音乐卡片发送角色语音             |
|       `BA_GAMEKEE_URL`        |  否  |   ...   |                   GameKee 数据源的地址                    |
|        `BA_SCHALE_URL`        |  否  |   ...   |                SchaleDB Json 数据源的地址                 |
|    `BA_SCHALE_MIRROR_URL`     |  否  |   ...   |                  SchaleDB 网页截图的地址                  |
|      `BA_BAWIKI_DB_URL`       |  否  |   ...   |                    bawiki-data 的地址                     |
|      `BA_ARONA_API_URL`       |  否  |   ...   |                  Arona Bot 数据源的地址                   |
|      `BA_ARONA_CDN_URL`       |  否  |   ...   |                  Arona Bot 图片 CDN 地址                  |
| `BA_CLEAR_REQ_CACHE_INTERVAL` |  否  |   `3`   |             插件清理请求缓存的间隔，单位小时              |
|  `BA_AUTO_CLEAR_ARONA_CACHE`  |  否  |   ...   | 是否在插件每次加载时自动清理从 Arona Bot 数据源缓存的图片 |

## 🎉 使用

### 指令表

兼容 [nonebot-plugin-PicMenu](https://github.com/hamo-reid/nonebot_plugin_PicMenu)

**现在 BAWiki 会自动帮你把 PicMenu 的字体设为系统已安装的字体，再也不需要麻烦的手动配置了，好耶~**

如果你不想用 PicMenu 的话，那么使用 `ba帮助` 指令即可；  
如果装载了 PicMenu，`ba帮助` 指令会调用 PicMenu 来生成帮助图片并发送

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [GameKee](https://ba.gamekee.com/) & [SchaleDB](https://lonqie.github.io/SchaleDB/) & [Arona Bot](https://doc.arona.diyigemt.com/api/)

- 插件数据源提供

<!--
### [RainNight0](https://github.com/RainNight0)

- 日程表 html 模板提供（已弃用）
-->

### `bawiki-data` 数据源贡献列表

- 见 [bawiki-data](http://github.com/lgc2333/bawiki-data)

## 💰 赞助

感谢各位大佬的投喂……！！本 fw 实在感激不尽……

- [爱发电](https://afdian.net/@lgc2333)
- <details>
    <summary>赞助二维码（点击展开）</summary>

  ![讨饭](https://raw.githubusercontent.com/lgc2333/ShigureBotMenu/master/src/imgs/sponsor.png)

  </details>

## 📝 更新日志

### 0.8.0

- 整理项目结构
- 添加内置帮助指令 `ba帮助`
- 添加 Arona Bot 数据源指令 `arona`
- 添加了配置项 `BA_ARONA_API_URL`、`BA_ARONA_CDN_URL`、`BA_CLEAR_REQ_CACHE_INTERVAL`、`BA_AUTO_CLEAR_ARONA_CACHE`
- 其他小更改（更换 `aiohttp` 为 `httpx` 等）

### 0.7.10

- 添加指令 `ba关卡`

### 0.7.9

- 添加配置项 `BA_VOICE_USE_CARD`

### 0.7.8

- 🎉 NoneBot 2.0 🚀

### 0.7.7

- 修复 bug

### 0.7.6

- 修复卡池为空不会提示的 bug

### 0.7.5

- 插件可以自动帮你配置 PicMenu 的字体了
- 给抽卡新增了冷却

### 0.7.2 ~ 0.7.4

- 修复 bug

### 0.7.1

- 更改配置项名称

### 0.7.0

- 修复 SchaleDB 源日程表出错的问题
- 添加了几个配置项，现在可以在 `.env` 文件中修改数据源链接了
- 修改了默认数据源链接
  - 买了七牛云的 CDN，设置的数据缓存 12 小时。不知道现在速度怎么样……
    希望不要有人故意搞我……  
    感谢大佬借用的已备案域名 [cyberczy.xyz](http://cyberczy.xyz/)！
- 其他小更改

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
- 新增请求接口的缓存机制，每 3 小时清空一次缓存
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
