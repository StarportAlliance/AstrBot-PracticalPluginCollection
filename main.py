from typing import cast

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools

from .entry import GlobalEntry
from .utils.message import MessageTemplate


class PracticalPluginCollection(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
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
            logger.warning(
                "插件全局开关已关闭，将不会进行任何操作。如果这不是预期行为，请检查你的插件配置。"
            )
        else:
            self.global_entry = await GlobalEntry.init(
                self.plugin_data_path,
                self.config,
                MessageTemplate(self.config["MessageTemplate"]),
            )
            logger.info("插件初始化完成。")

    async def terminate(self):
        logger.info("插件已终止。")

    def _event_filter(self, event: AstrMessageEvent) -> bool:
        """事件过滤器。

        Args:
            event (AstrMessageEvent): 事件对象。

        Returns:
            bool: 如果通过检查则返回 True，否则返回 False。
        """
        if not self.config["GlobalEnable"]:
            return False
        if self.global_entry.ban.check_user_is_banned(event.get_sender_id()):
            return False
        user_id = event.get_sender_id()
        group_id = event.get_group_id()
        request_type = event.get_message_type().value
        whitelist_config = self.config["Whitelist"]
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
                logger.debug(f"判断事件类型 {request_type} 失败，将忽略此事件处理。")
                return False

    @filter.command_group("ban")
    def ban(self):
        """封禁系统功能命令组。"""

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    @filter.permission_type(filter.PermissionType.ADMIN)
    @ban.command("add")
    async def add_ban(self, event: AstrMessageEvent, user_id: str, reason: str = ""):
        """新增封禁用户。"""
        if not self._event_filter(event):
            return
        yield self.global_entry.ban.add(event, user_id, reason)

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    @filter.permission_type(filter.PermissionType.ADMIN)
    @ban.command("remove")
    async def remove_ban(self, event: AstrMessageEvent, user_id: str):
        """解封给定用户。"""
        if not self._event_filter(event):
            return
        yield self.global_entry.ban.remove(event, user_id)

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    @filter.permission_type(filter.PermissionType.ADMIN)
    @ban.command("list")
    async def list_ban(self, event: AstrMessageEvent):
        """列出所有封禁用户。"""
        if not self._event_filter(event):
            return
        yield self.global_entry.ban.list(event)

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    async def group_request_review(self, event: AstrMessageEvent):
        """加群请求自动审核模块事件接收器。"""
        if not self._event_filter(event):
            return
        if not self.module_config["GroupRequestReview"]["Enable"]:
            return
        await self.global_entry.group_request_review.handle_request_review(event)

    @filter.platform_adapter_type(filter.PlatformAdapterType.AIOCQHTTP)
    @filter.command("like")
    async def like(self, event: AstrMessageEvent, times: int = 10):
        """赞我！"""
        if not self._event_filter(event):
            return
        if not self.module_config["EnableSendLike"]:
            return
        yield await self.global_entry.send_like.like(event, times)
