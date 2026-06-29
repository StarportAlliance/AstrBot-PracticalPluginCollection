from astrbot.api.star import Context, Star, StarTools
from astrbot.api import logger, AstrBotConfig
from astrbot.api.event import filter, AstrMessageEvent
from .core import BanSystem, EconomicSystem
from .module import handle_request_review
from .module.group_request_review.log import GroupRequestLog
from typing import cast


class PracticalPluginCollection(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.context = context
        """插件上下文对象。"""
        self.config = config
        """插件配置。"""
        self.module_config = cast(dict, self.config["ModuleConfig"])
        """插件模块配置。"""
        self.plugin_data_path = StarTools.get_data_dir()
        """插件数据目录。"""

    # 这是一个 TODO，计划中会使用该方法去创建定时任务。
    # 限定 on_platform_loaded 后再创建是为了利用该 Hook 拿到 CQHTTP 平台客户端实例
    # @filter.on_platform_loaded()
    # async def scheduled_task(self, event: AstrMessageEvent):
    #     """定时任务启动器。"""

    async def initialize(self):
        """初始化插件。"""
        if not self.config["GlobalEnable"]:
            logger.info(
                "插件全局开关已关闭，将不会进行任何操作。如果这不是预期行为，请检查你的插件配置。"
            )
        else:
            self.ban_system = await BanSystem.init(self.plugin_data_path)
            self.economic_system = await EconomicSystem.init(self.plugin_data_path)
            self.group_request_log = await GroupRequestLog.init(self.plugin_data_path)
            logger.info("插件初始化完成。")

    async def terminate(self):
        logger.info("插件已终止。")

    def _event_filter(self, event: AstrMessageEvent, whitelist_config: dict) -> bool:
        """事件过滤器。

        Args:
            event (AstrMessageEvent): 事件对象。
            whitelist_config (dict): 插件白名单配置对象。

        Returns:
            bool: 如果通过检查则返回 True，否则返回 False。
        """
        if not self.config["GlobalEnable"]:
            return False
        user_id = event.get_sender_id()
        group_id = event.get_group_id()
        request_type = event.get_message_type().value
        match request_type:
            case "GroupMessage":  # 群聊
                return group_id in whitelist_config["WhitelistGroups"]
            case "FriendMessage":
                raw_message = cast(dict, event.message_obj.raw_message)
                if raw_message.get("sub_type", "") == "group":  # 临时会话
                    return (
                        whitelist_config["AllowTemporaryConversationFromAllowedGroup"]
                        and group_id in whitelist_config["WhitelistGroups"]
                    )
                else:  # 私聊
                    return user_id in whitelist_config["WhitelistFriends"]
            case _:  # 由于 aiocqhttp 不存在 OTHER_MESSAGE 类型事件，因此此处将其和其他可能的未知类型一并处理
                logger.warning(
                    f"判断事件类型 {request_type} 失败，这似乎不是 Onebot 11 的标准事件类型。请检查插件是否兼容当前 AstrBot / NapCat 版本。"
                )
                return False

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    async def group_request_review(self, event: AstrMessageEvent):
        """加群请求自动审核模块事件接收器。"""
        if not self._event_filter(event, self.config["Whitelist"]):
            return
        await handle_request_review(
            event,
            self.module_config["GroupRequestReview"],
            self.ban_system,
            self.group_request_log,
        )

    @filter.command_group("ban")
    def ban(self):
        """封禁系统功能命令组。"""

    @ban.command("add")
    async def add_ban(
        self, event: AstrMessageEvent, user_id: int, reason: str = "", duration: int = 0
    ):
        """添加封禁。"""
        try:
            async for result in self.ban_system.add(event, user_id, reason, duration):
                yield result
        except Exception:
            logger.exception(
                f"处理命令 `/ban add {user_id} {reason} {duration}` 时发生错误。"
            )

    @ban.command("remove")
    async def remove_ban(self, event: AstrMessageEvent, user_id: int):
        """解封给定用户。"""
        try:
            async for result in self.ban_system.remove(event, user_id):
                yield result
        except Exception:
            logger.exception(f"处理命令 `/ban remove {user_id}` 时发生错误。")
