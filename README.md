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

### Tip

- 本插件并不自带 `balogo` 指令需要的字体，请自行下载并安装到系统：  
  [RoGSanSrfStd-Bd.otf](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/bawiki/RoGSanSrfStd-Bd.otf)、[GlowSansSC-Normal-v0.93.zip](https://github.com/welai/glow-sans/releases/download/v0.93/GlowSansSC-Normal-v0.93.zip)

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

在 nonebot2 项目的 `.env` 文件中添加下表中的配置

|            配置项            | 必填 | 默认值  |                                         说明                                          |
| :--------------------------: | :--: | :-----: | :-----------------------------------------------------------------------------------: |
|          `BA_PROXY`          |  否  | `None`  |                              访问各种数据源时使用的代理                               |
|     `BA_GACHA_COOL_DOWN`     |  否  |   `0`   |                              每群每人的抽卡冷却，单位秒                               |
|     `BA_VOICE_USE_CARD`      |  否  | `False` |                          是否使用自定义音乐卡片发送角色语音                           |
|     `BA_USE_FORWARD_MSG`     |  否  | `True`  |                             是否使用合并转发发送部分消息                              |
|   `BA_SCREENSHOT_TIMEOUT`    |  否  |  `60`   |                                 网页截图超时，单位秒                                  |
|  `BA_DISABLE_CLASSIC_GACHA`  |  否  | `False` |                      抽卡次数 10 次以下时是否不使用经典抽卡样式                       |
|        `BA_GACHA_MAX`        |  否  |  `200`  |                                   单次抽卡最大次数                                    |
|      `BA_ILLEGAL_LIMIT`      |  否  |   `3`   |            用户在长对话中非法操作多少次后直接结束对话，填 `0` 以禁用此功能            |
| `BA_ARONA_SET_ALIAS_ONLY_SU` |  否  | `False` |                    是否只有超级用户才能修改 `arona` 指令所用的别名                    |
|       `BA_GAMEKEE_URL`       |  否  |   ...   |                                 GameKee 数据源的地址                                  |
|       `BA_SCHALE_URL`        |  否  |   ...   |                              SchaleDB Json 数据源的地址                               |
|      `BA_BAWIKI_DB_URL`      |  否  |   ...   |                                  bawiki-data 的地址                                   |
|      `BA_ARONA_API_URL`      |  否  |   ...   |                                Arona Bot 数据源的地址                                 |
|      `BA_ARONA_CDN_URL`      |  否  |   ...   |                                Arona Bot 图片 CDN 地址                                |
|     `BA_SHITTIM_API_URL`     |  否  |   ...   |                                   什亭之匣 API 地址                                   |
|       `BA_SHITTIM_URL`       |  否  |   ...   |                                     什亭之匣网址                                      |
|    `BA_SHITTIM_DATA_URL`     |  否  |   ...   |                                   什亭之匣数据地址                                    |
|       `BA_SHITTIM_KEY`       |  否  | `None`  |            什亭之匣 API Key（获取途径 [看这里](https://arona.icu/about)）             |
|  `BA_SHITTIM_REQUEST_DELAY`  |  否  |   `0`   |                   请求什亭之匣 API 后的等待时间，用于测试时限制 QPS                   |
|        `BA_REQ_RETRY`        |  否  |   `1`   | 每次请求的重试次数<br />当值为 `1` 时，总共会请求两次（请求一次，重试一次），以此类推 |
|      `BA_REQ_CACHE_TTL`      |  否  | `10800` |                              请求缓存的过期时间，单位秒                               |
|  `BA_SHITTIM_REQ_CACHE_TTL`  |  否  |  `600`  |                        什亭之匣相关请求缓存的过期时间，单位秒                         |
|       `BA_REQ_TIMEOUT`       |  否  | `10.0`  |                       请求超时，单位秒，为 `None` 表示永不超时                        |
|  `BA_AUTO_CLEAR_CACHE_PATH`  |  否  | `False` |                        是否在插件每次加载时自动清理缓存文件夹                         |

<!--
由于 CDN 可能并不给力，如果有条件的话本人推荐使用代理直接访问原地址，下面是对应 `.env` 配置：

```ini
BA_PROXY=http://127.0.0.1:7890
BA_SCHALE_URL=https://schale.gg/
BA_SCHALE_MIRROR_URL=https://schale.lgc2333.top/
BA_BAWIKI_DB_URL=https://bawiki.lgc2333.top/
```
-->

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

### [GameKee](https://ba.gamekee.com/) &<br />[SchaleDB](https://lonqie.github.io/SchaleDB/) &<br />[Arona Bot](https://doc.arona.diyigemt.com/api/) &<br />[什亭之匣](https://arona.icu/)

- 插件数据源提供

### [nulla2011/Bluearchive-logo](https://github.com/nulla2011/Bluearchive-logo)

- 蔚蓝档案标题生成器

<!--
### [RainNight0](https://github.com/RainNight0)

- 日程表 html 模板提供（已弃用）
-->

### `bawiki-data` 数据源贡献列表

- 见 [bawiki-data](https://github.com/lgc-NB2Dev/bawiki-data)

## 💰 赞助

感谢各位大佬的投喂……！！本 fw 实在感激不尽……

- [爱发电](https://afdian.net/@lgc2333)
- <details>
    <summary>赞助二维码（点击展开）</summary>

  ![讨饭](https://raw.githubusercontent.com/lgc2333/ShigureBotMenu/master/src/imgs/sponsor.png)

  </details>

## 📝 更新日志

### 0.10.3

- 删除指令 `ba总力排名`
- 其他小更改

### 0.10.2

- 为 `ba小心卷狗` 和 `ba爱丽丝的伙伴` 指令图添加难度显示
- 修改帮助文案，新增指令别名 `ba总力档线` -> `ba档线`、`ba总力排名` -> `ba排名`

### 0.10.1

- 修复 `ba总力档线` 指令返回图片中更新时间显示时区错误的问题
- 新增配置项 `BA_ILLEGAL_LIMIT`、`BA_ARONA_SET_ALIAS_ONLY_SU`、`BA_SHITTIM_REQ_CACHE_TTL`

### 0.10.0

- 新增 [什亭之匣](https://arona.icu/) 相关内容
- 为 Arona 指令添加了添加、删除别名功能
- 前瞻图默认列表个数改为 `3`
- 为 `ba语音` 和 `ba漫画` 指令加上了列表选择
- `ba学生wiki` 指令现在不显示学生语音列表了
- 修改了 SchaleDB 的学生生日展示样式
- 内置帮助指令以图片方式展示结果
- 更新主线攻略查询地址
- 配置项更改：
  - 添加 `BA_USE_FORWARD_MSG`
  - 添加 `BA_REQ_RETRY`
  - 添加 `BA_REQ_CACHE_TTL`
  - 添加 `BA_REQ_TIMEOUT`
  - 添加 `BA_SHITTIM_URL`
  - 添加 `BA_SHITTIM_API_URL`
  - 添加 `BA_SHITTIM_DATA_URL`
  - 添加 `BA_SHITTIM_KEY`
  - 添加 `BA_SHITTIM_REQUEST_DELAY`
  - 删除 `BA_CLEAR_REQ_CACHE_INTERVAL`
  - 重命名 `BA_AUTO_CLEAR_ARONA_CACHE` -> `BA_AUTO_CLEAR_CACHE_PATH`
- 其他代码重构，Bug 修复 ~~，新增了一些 Bug（可能）~~

<details>
<summary><strong>未来将更新（点击展开）</strong></summary>

### 1.0.0

- 使用 `nonebot-plugin-alconna` 实现多适配器支持

### 0.11.0

- 使用 `playwright` 重构现有的 Pillow 绘图

</details>

<details>
<summary><strong>历史更新日志（点击展开）</strong></summary>

### 0.9.7

- 修复 `balogo` 的 fallback 字体的字重问题

### 0.9.6

- 新增指令 `balogo`

### 0.9.5

- 修复由于 SchaleDB 数据结构变动导致的一些 Bug
- 抽卡总结图现在有半透明和圆角了

### 0.9.4

- 修复了三星爆率过高的 bug ([#47](https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki/pull/47))

### 0.9.3

- 微调 `ba日程表` 指令：GameKee 源的日程表现在可以分服务器展示了，顺便修复了 SchaleDB 源日程的 Bug，详见指令帮助
- 现在在抽卡次数为 10 次以下时，默认使用经典抽卡样式（旧版的还原游戏的抽卡样式）
- 配置项变更：
  - 添加 `BA_DISABLE_CLASSIC_GACHA`

### 0.9.2

- `ba切换卡池` 指令现在不带参数时会显示所有卡池以供切换了

### 0.9.1

- 重构抽卡绘图部分、数据源没有池子数据时自动使用常驻池
- 将阿罗娜的回复变得更二次元了
- 配置项变更：
  - 添加 `BA_GACHA_MAX`

### 0.9.0

- 更新了 SchaleDB 页面的截图处理方式，现在可以支持源站与任何镜像了
- 添加国服前瞻获取，详见指令 `ba千里眼` 帮助
- 由于 CDN 域名过期，修改了默认源到原源
- 尝试修复 [#43](https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki/issues/43) 与 [#46](https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki/issues/46)
- 配置项变更：
  - 删除 `BA_SCHALE_MIRROR_URL`
  - 添加 `BA_SCREENSHOT_TIMEOUT`

### 0.8.6

- 修复 [#39](https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki/issues/39)
- 尝试修复 [#45](https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki/issues/45)

### 0.8.5

- 修复 [#41](https://github.com/lgc-NB2Dev/nonebot-plugin-bawiki/issues/41)
- 配置项 `BA_AUTO_CLEAR_ARONA_CACHE` 默认值改为 `False`

### 0.8.4

- 现在会对 GameKee 的日程表分页了
- `ba羁绊` 指令带图发送失败时会提醒用户
- 修复 `ba学生wiki` 截图失败的 bug，同时优化截图样式
- 漫画获取不再依赖 bawiki-data 数据源，现在直接从 GameKee 现爬；加入了搜索漫画功能，并且图片过多会使用合并转发的方式发送

### 0.8.3

- 修改缓存路径

### 0.8.2

- 修改了 `ba语音` 指令的特性，兼容了有中配语音的学生，请查看该指令帮助获取详细信息
- 删除了 `arona` 指令模糊搜索展示类别的功能，因为模糊搜索时 `type` 固定为 `0` 了

### 0.8.1

- 使用 `arona` 指令模糊搜索的时候会显示图片类别了

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

</details>
