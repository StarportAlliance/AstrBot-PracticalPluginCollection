# AGENTS.md

PracticalPluginCollection 是 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 的实用插件合集，旨在集成多个模块并将其封装为一个统一插件，并通过多功能互联等改进来提供更统一流畅的使用体验。
> AstrBot 是一个开源的一体化代理聊天机器人平台，与主流即时通讯应用集成。它为个人、开发者和团队提供可靠且可扩展的对话式人工智能基础设施。

项目目前仍在早期开发阶段（v0）。

## 技术栈

| 类别       | 技术                            | 说明                                                    |
| ---------- | ------------------------------- | ------------------------------------------------------- |
| 编程语言   | Python ~= 3.12.0                | 使用 Python 3.12，且无需考虑旧版兼容                    |
| 机器人框架 | AstrBot >= 4.17.6               | 基于 `Star` 类开发的一体化聊天机器人插件                |
| 协议适配   | aiocqhttp（NapCat / OneBot 11） | 通过 NapCat 协议端与 QQ 交互                            |
| 数据存储   | aiosqlite >= 0.22.1             | 用于核心与模块本地数据持久化                            |
| 包管理器   | uv                              | 现代 Python 包管理器，使用 `pyproject.toml` + `uv.lock` |
| 代码检查   | ruff >= 0.15.13                 | 开发依赖，用于代码风格与质量检查                        |
| 许可证     | AGPL-3.0-or-later               | 强 copyleft 许可证                                      |
| 支持平台   | aiocqhttp                       | 仅考虑支持 NapCat/Onebot 11 协议端                      |

## 编码要求

- CodeGraph 是一个预构建的知识图谱，包含代码库中每个符号、调用边和依赖关系。你应在开始任务前先调用 CodeGraph 工具（`codegraph_explore`）以获取项目的知识图谱，尽量避免通过文件搜索来获取代码信息。
  - 如果你没有相关工具可调用，请先用文件搜索方式获取代码信息，在完成任务时明确告知用户 CodeGraph 工具不可用，并引导用户前往 https://github.com/colbymchenry/codegraph 安装 CodeGraph。

## 开发提示

- 项目虽已安装 Ruff，但并非必须要在完成任务后跑一遍 Ruff check。除非用户主动要求，一般情况下你可以偷懒不 Check。