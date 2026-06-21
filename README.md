![astrbot_practical_plugin_collection](https://socialify.git.ci/QingFeng-awa/astrbot_practical_plugin_collection/image?description=1&font=KoHo&language=1&name=1&pattern=Solid&theme=Auto)

<div align="center">
<h1>Practical Plugin Collection</h1>
<p>AstrBot 实用插件合集</p>
</div>

> [!Note]
> 项目仍处于早期开发阶段，各项内容还尚未完善。

## 介绍

PracticalPluginCollection 是 [AstrBot](https://astrbot.app) 的实用插件合集，旨在集成多个插件并将其封装为一个统一插件，并通过改写代码等实现多功能互联来提供更统一流畅的使用体验。

### ...为什么？

原本我是使用 Zerobot-Plugin (zbp) 项目的，这个项目是一个 Zerobot 插件合集，集成了大量插件。\
但毕竟 zbp 是基于 Zerobot 的，而我更希望使用 AstrBot，我不喜欢同时接入多个机器人框架，这可能会导致机器人左右脑互搏（功能冲突）；zbp 还将仓库分为了超多仓库/module，我不否认这样做可以带来一些好处，但恕我无法接受改一个功能要翻几个仓库。\
此外 zbp 几乎把日志功能当空气，项目几乎没有日志记录，出现错误直接将错误信息发送给用户，好比：
```py
except Exception as e:
    await event.send(e)
```
错误堆栈一个没有，上下文也没有日志，要给你报个`ERROR: unknown`我怎么知道问题出在哪里？

综上所述，最终我决定自己从零写个 AstrBot 版本的 zbp，并将其命名为 PracticalPluginCollection。