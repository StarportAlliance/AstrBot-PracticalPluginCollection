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
  - [x] 银行系统
  - [ ] Plugin Pages
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
  - [ ] 打劫（robbery）
  - [ ] 猜单词（wordle）
  - [ ] 钓鱼（fish）
  - And More...

## 安装

在 AstrBot 插件管理页面点击右下角 + 按钮（安装插件），选择`从链接安装`，复制粘贴本仓库 URL，点击安装即可。

### 更新

很遗憾，AstrBot 目前对 GitHub Release 的支持并不完善，您暂时无法快捷的升降级插件。\
我们建议您先卸载当前插件但保留插件数据，随后跟随安装教程重新安装本插件，AstrBot 会自动安装 Release 中最新（可能非稳定）版本的插件。\
或者，您也可以选择插件管理页中插件卡片更多菜单中的重新安装选项，但该选项会强制使用最新 Commit，您可能会安装到尚未完成的开发版本。

## 鸣谢

- [FloatTech/ZeroBotPlugin](https://github.com/FloatTech/ZeroBot-Plugin) - 项目及模块灵感来源
- [sealdice/sealdice-core](https://github.com/sealdice/sealdice-core) - 模块灵感来源
- [Zhalslar/astrbot_plugin_box](https://github.com/Zhalslar/astrbot_plugin_box) - 模块灵感来源
- [qiqi55488/astrbot_plugin_appreview](https://github.com/qiqi55488/astrbot_plugin_appreview) - 模块灵感来源
- [huntuo146/astrbot_plugin_Group-Verification_PRO](https://github.com/huntuo146/astrbot_plugin_Group-Verification_PRO) - 模块灵感来源
- [DeepSeek](https://www.deepseek.com) - 技术支持。这里吐槽一下 AstrBot 的开发文档内容部分过时且不全，导致我不得不消耗自己的 Token 跟 AI 探讨框架源码。
