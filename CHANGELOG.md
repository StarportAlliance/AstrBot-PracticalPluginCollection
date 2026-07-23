## v0.5.1

### New

- 封禁系统解封用户时将校验用户是否已存在黑名单中，同步新增要解封用户不存在时发送的消息模板配置。
- 新增进退群提醒模块。
- 新增今日人品模块。

### Fix

- 添加了 `requirements.txt`，若部分极端环境没有安装插件所需依赖的情况下 AstrBot 现将会自动安装依赖了。
  - 之所以极端是因为 AstrBot 本体就要求这个依赖，理论上没装你连 AstrBot 都跑不起来。
- 补充了对加群请求审核模块的异常处理。

---

关于本插件完整更新日志，请参阅 [GitHub Releases](https://github.com/StarportAlliance/AstrBot-PracticalPluginCollection/releases)。