## v0.4.0

> [!Warning]
> ### Breaking Change
> - 更改了赞我模块插件开关的配置项，您可能需要在更新后重新配置该模块配置。

### New

- 赞我模块新增对点赞次数已达今日上限的情况的处理，支持自定义返回文本。
- 赞我模块点赞成功消息模板新增 `{times}`（尝试点赞次数）支持。
- 模块支持按需加载，当功能被关闭时将不会初始化相关实例，减少资源负载。

### Fix

- 修复赞我命令无响应的问题。
- 修复了加群请求审核模块工作异常的问题。
- 修复了赞我模块开关未正常工作的问题。

---

关于本插件完整更新日志，请参阅 [GitHub Releases](https://github.com/StarportAlliance/AstrBot-PracticalPluginCollection/releases)。