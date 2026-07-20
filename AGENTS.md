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

### 新增一个模块

模块可以指核心功能也可以指模块功能。一个模块的标准模版是这样的：
```py
from ...utils.message.msg import MessageTemplate # MessageTemplate 实际引用路径视实际情况而定，这里假定文件位于 `/module/<ModuleName>/main.py`。

class Module:
    """功能模块。""" # “功能”是名称，“模块”是固定后缀。如果是核心功能则不需要这个后缀。但核心功能一般是某种“系统”，虽然并非强制，但一般都以“系统”作后缀，例如现有的封禁系统、银行系统。

    _msg_template: MessageTemplate # 消息模板类，需要从 config 中获取消息模版时使用。非必需，用不上可以不加。

    def __init__(self, msg_template: MessageTemplate):
        """初始化功能模块。

        Args:
            msg_template: 消息模板类。
        """
        self._msg_template = msg_template
```

### 结构定义

我们将一个功能分为 3 个部分：

#### 入口 handler（第一层/顶层）

插件 Event Listener 与 Command Handler 的定义位置，（受限于 AstrBot 框架的限制）位于根目录的 `main.py` 文件中。
该层仅作薄包装，不含任何实际逻辑，此处应当将其转发至中层的核心业务逻辑。

#### 主业务逻辑（第二层/中层）

主业务逻辑实际也分两层。

##### 业务核心逻辑

对应功能的核心业务代码逻辑，分布于各个核心/模块中，功能的核心逻辑均在此处实现，顶层正是将事件转发至该层定义的方法。
一般情况下，该层方法所在的文件名称应当是 `main.py`（Event Listener / Command Handler）或 `command.py`（Command Handler）。

所有业务核心逻辑方法应当仅返回以下值：
- `MessageEventResult`：消息事件结果。return 给顶层，顶层再 yield 供 AstrBot 消费；
- `None`：不返回任何内容。

通常一般只返回上述值其一，当然也可以两者都返回，但不能返回其他值。

##### 业务底层接口

为了更好的可读性与可维护性，我们会适当的将部分可复用的或不影响代码连贯性的逻辑代码从核心逻辑中提取为一个单独的方法，这些方法被称为业务底层接口。

#### 通用底层接口（第三层/底层）

底层接口指 `utils` 模块中的方法。
实现底层接口或将其从中层提取时，你应当确认其是通用的，会被多个模块/方法/函数调用的，否则请保持内联代码。
> 但存在例外，`utils.api` 的类 `ProtocolEndApi` 不需要受“方法须通用”的规则限制，所有请求协议端 API（CQHTTP.AsyncApi）的操作均应调用此类包装过后的方法。非 `utils` 目录中的方法不视为底层接口，同样也不需要遵循上述规则。

### 功能设计

我们使用面向对象式设计，即将功能封装为一个类。
我们将实例所需的基础资源与运行时传参分离，一般情况下，你应当在实例初始化时就准备好所有基础资源。
例如：
```py
class Module:

    _msg_template: MessageTemplate
    """消息模板。"""

    def __init__(self, msg_template: MessageTemplate):
        self._msg_template = msg_template

    async def handler(self, event: AstrMessageEvent) -> MessageEventResult:
        return event.plain_result(self._msg_template.get_msg_template(...))
```

### 方法编写规范

#### 文档注释

所有函数/方法均应包含文档注释，使用 Google Python 注释规范。但位于根目录的 `main.py` 为例外，该文件不需要必须遵守本条规则。

- `Args`、`Yields`、`Returns` 字段若存在对应参数则必须包含，否则可省略。
- 若需使用特殊方法调用方法，则必须包含 `Examples` 字段用以演示。
- `Raises` 字段若主动引发了相关异常则必须包含，可能由用户输入传参不当极易高发的异常也应当说明，否则可省略。主动引发但被自行捕获的异常不需要标注。
- 不应包含 `Notes` 字段，有需要请写在描述部分内。

#### 返回值类型注解

对于有返回值的函数/方法必须明确注解返回值类型，但返回值为类实例的除外，对于此种不应添加注解。
对于返回值有且仅有 None 的函数/方法，不应添加类型注解。
对于一次性操作，除非现有设计需要，否则不应返回任何值而**仅仅为了**表明操作已成功完成。

#### 异常处理

对于非业务核心逻辑，不应捕获异常仅是为了日志后重抛，也不应在发生异常时试图返回默认值。一般情况下尽量避免添加日志。
对于核心业务逻辑，我们统一使用以下异常处理方法：
```py
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult


# Command Handler
async def command_handler(self, event: AstrMessageEvent) -> MessageEventResult:
    try:
        ...
    except Exception:
        logger.exception(f"xxx 时发生错误。")
        return event.plain_result(
            self._msg_template.get_msg_template("General", "UnknownError")
        ) # _msg_template 为 utils.message.MessageTemplate 类的实例，确保你在功能类实例化时传递了相关参数
# Event Listener
async def event_listener(self, event: AstrMessageEvent):
    try:
        ...
    except Exception:
        logger.exception(f"xxx 时发生错误。")
```

#### 日志输出

所有日志输出应当仅通过 astrbot.api 暴露的 `logger` 实例进行。
可用日志等级有 5 个：
- `DEBUG`：调试日志。在可能需要调试的位置时可适当使用。
- `INFO`：信息日志。在重要操作发生后可使用该日志输出一条提示信息。
- `WARNING`：警告日志。当遇到插件可预见但无法处理/不符合常规情况时可使用该日志进行警告。
- `ERROR`：错误日志。插件发生错误时使用该日志进行记录。要注意一般情况下我们使用 logger.exception 以记录完整异常信息，仅当异常时被人为引发时再考虑选择使用 logger.error。
- `CRITICAL`：致命异常。仅在插件因该错误导致无法启动时才使用该日志进行记录。该日志仅可在 `main.py` 中的 `__init__` / `initialize` 方法中使用，且一般情况下后面会跟 raise 以将异常重抛给 AstrBot。

尽量在非核心业务逻辑中避免使用 INFO 级及以下的日志，出现错误时不处理或直接 raise。
如果没有必要 raise，可以返回 falsey 值（使上层逻辑退出）并输出警告日志。

#### 属性访问

访问对象固定（已知）属性时使用点号操作符（`.`），否则均使用方括号（`[]`）。
仅当访问对象**确定可能为空**时才使用 `.get()` 方法，且通过该方法仅是为了不报错，不应作为回滚值。

### 规则豁免

编码要求在适当情况下可以绕过。如果某个地方**确实因为需要**而**不得不**违反要求，只需在一旁写个注释，合理说明为什么要这么做即可。

## 开发提示

- 项目虽已安装 Ruff，但并非必须要在完成任务后跑一遍 Ruff check。除非用户主动要求，一般情况下你可以偷懒不 Check。
- 如果需要，可以翻阅 `.venv\Lib\site-packages\astrbot\` 下文件了解 AstrBot 源码中的相关实现。