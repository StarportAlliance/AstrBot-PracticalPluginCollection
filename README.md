![astrbot_practical_plugin_collection](https://socialify.git.ci/QingFeng-awa/astrbot_practical_plugin_collection/image?description=1&font=KoHo&language=1&name=1&pattern=Solid&theme=Auto)

> [!Warning]
> 当前项目为**早期开发阶段**，可能每个新版本都会存在破坏性变更，且不会编写自动迁移代码，请自行做好相关准备。

## 介绍

PracticalPluginCollection 是 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 的实用插件合集，旨在集成多个模块并将其封装为一个统一插件，并通过多功能互联等改进来提供更统一流畅的使用体验。

## 功能

> 详细文档目前仍处于计划中。

- 核心 (Core) 功能
  - [ ] 帮助菜单
  - [x] 封禁系统
  - [x] 经济系统
  - And More...
- 模块 (Module) 功能
  - [x] 加群自动审核（group_request_review）：提供了基于正则表达式的加群自动处理功能，能够通过正则判断入群答案从而自动同意/拒绝请求，支持等级/速率限制等筛选条件。
  - [ ] 简易入群人机验证（simple_captcha）
  - [ ] 群老婆（qq_wife）
  - [ ] 今日人品（daily_luck）
  - [ ] 我超，盒！（box）
  - [ ] B 站链接解析（bilibili_link_parser）
  - [x] 赞我（send_like）：让机器人点赞你的资料卡。
  - [ ] 签到（check_in）
  - [ ] 彩票（lottery）
  - [ ] 磕 cp（show_affection）
  - [ ] 入/退群提醒（welcome_goodbye）
  - And More...

## 安装

在 AstrBot 插件管理页面点击右下角 + 按钮（安装插件），选择`从链接安装`，复制粘贴本仓库 URL，点击安装即可。

## 为什么？

原本我是使用 ZeroBot-Plugin (zbp) 的，这个项目是一个 ZeroBot 插件合集，集成了大量插件，从结果来看我其实很认可这个项目。\
但遗憾的是 zbp 毕竟是基于 ZeroBot 而非 AstrBot，我是不喜欢同时使用两个框架的。\
此外 zbp 让我无法接受的点是将一个项目分为了超多仓库/module，可能开发团队这么做确有他们的用意，但恕我无法接受改一个功能要翻几个仓库。而且 zbp 还几乎把日志功能当空气，项目几乎没有日志记录，出现错误直接将错误信息发送给用户，好比：
```py
except Exception as e:
    await event.send(e)
```
错误堆栈一个没有，上下文也没有日志，报个`ERROR: unknown`我怎么知道问题出在哪里？

综上所述，最终我决定创建这个项目，命名为 PracticalPluginCollection，目标就是打造一个 AstrBot 版本的 zbp。

## 鸣谢

- [FloatTech/ZeroBotPlugin](https://github.com/FloatTech/ZeroBot-Plugin) 提供了本项目及部分模块的灵感来源。
- [Zhalslar/astrbot_plugin_box](https://github.com/Zhalslar/astrbot_plugin_box) 提供了本项目模块 `box` 的灵感来源。
- [qiqi55488/astrbot_plugin_appreview](https://github.com/qiqi55488/astrbot_plugin_appreview) 提供了本项目模块 `group_request_review` 的灵感来源。
- [huntuo146/astrbot_plugin_Group-Verification_PRO](https://github.com/huntuo146/astrbot_plugin_Group-Verification_PRO) 提供了本项目模块 `simple_captcha` 的灵感来源。
- [sealdice/sealdice-core](https://github.com/sealdice/sealdice-core) 提供了本项目模块 `daily_luck` 的灵感来源。
