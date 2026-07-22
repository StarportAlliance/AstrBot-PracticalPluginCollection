# 贡献指南

## Vibe Coding 使用准则

我们并不介意使用 AI 来辅助编程，AI 确实好用。\
但在使用 Vibe Coding 时，您必须确保所有代码均已被人工审查，均符合项目标准。\
Vibe Coding 应当为辅，而非占据主导地位。若你发起的 PR 有 75%+（±10%）的代码为 AI 生成，你将被本组织拉黑。

## 快速开始

我们使用 [uv](https://docs.astral.sh/uv/) 管理依赖，确保你的环境中已安装 uv。\
使用 uv 即可快捷的初始化虚拟环境并安装项目依赖：
```bash
uv sync --frozen
```

> `--frozen` 选项将不更新锁文件（`uv.lock`）。如果你只是为了向我们发起 PR，这通常可以避免产生不必要的更改被添加到 Commit。

此外，我们强烈建议你使用 [VSCode](https://code.visualstudio.com) 作为代码编辑器，我们的工作区设置均针对 VSCode 设置。基于 VSCode 的 AI IDE 也受推荐，例如 [Trae CN](https://www.trae.cn/ide)、[Cursor](https://cursor.com/cn)。这些 AI IDE（通常）会自动将 `AGENTS.md` 自动添加至上下文中，使你所用的 AI 直接了解项目信息与编码规则。\
VSCode 工作区设置中已配置了推荐的扩展程序，为了更好的开发体验同时能够通过项目验收标准，我们强烈建议你安装。\
——不过 Ruff 和 Pylance 的功能上有一些冲突，前者实际上主要是用于格式化代码的，如果你不用 VSCode 的格式化功能而更喜欢自己运行 `ruff format`，你也可以选择不安装 Ruff。

## 编码要求

请参阅 [AGENTS.md](AGENTS.md) 中的编码要求章节。

这里还有额外的要求：
- 所有代码需在 Pylance Standard 模式下做到无任何报错、警告，且通过 Ruff 检查。

## 开发提示

- 项目仓库内包含了 AstrBot Plugin Reviewer 和 AstrBot Skill，前者为 AstrBot 插件市场审查器的 Skill 版本，在你准备 Commit 前可以让 AI 调用这个 Skill 以官方插件市场审查规范及回复风格来 review 你的更改；后者则是 [xunxiing/AstrBot-Skill](https://github.com/xunxiing/AstrBot-Skill) 提供的 AstrBot Agent Skill，包含插件开发的结构化技术文档，这个 Skill 似乎是基于 AstrBot 源码生成而非照搬文档，让 AI 调用此 Skill 可能比引用在线文档可靠。