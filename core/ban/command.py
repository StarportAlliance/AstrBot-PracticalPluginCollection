from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult

from ...utils.message import MessageTemplate
from .main import BanSystemCore


class BanSystem(BanSystemCore):
    """封禁系统。"""

    _msg_template: MessageTemplate
    """消息模板类。"""
    _config: AstrBotConfig
    """插件配置对象。"""

    def __init__(self, config: AstrBotConfig, msg_template: MessageTemplate):
        """初始化封禁系统。

        Args:
            config (AstrBotConfig): 插件配置对象。
            msg_template (MessageTemplate): 消息模板类。
        """
        super().__init__(config["CoreConfig"]["BanSystem"])
        self._msg_template = msg_template
        self._config = config
        logger.info("封禁系统初始化完成。")

    def add(
        self,
        event: AstrMessageEvent,
        user_id: str,
        reason: str = "",
    ) -> MessageEventResult:
        """添加封禁用户。

        Args:
            event (AstrMessageEvent): 消息事件对象。
            user_id (str): 用户 ID。
            reason (str, optional): 封禁原因。

        Returns:
            MessageEventResult: 封禁结果消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            ban_system = BanSystem(config, msg_template)
            yield ban_system.add(event, "123456789", "测试封禁")
            ```
        """
        try:
            if self.add_ban(user_id, reason):
                self._config.save_config()
                logger.info(f"已封禁用户 {user_id}。")
                return event.plain_result(
                    self._msg_template.get_msg_template(
                        "BanSystem", "AddNewBan", user_id=user_id
                    )
                )
            else:
                return event.plain_result(
                    self._msg_template.get_msg_template(
                        "BanSystem", "DuplicateBan", user_id=user_id
                    )
                )
        except Exception:
            logger.exception("添加封禁用户时发生错误。")
            raise

    def remove(
        self,
        event: AstrMessageEvent,
        user_id: str,
    ) -> MessageEventResult:
        """移除封禁用户。

        Args:
            event (AstrMessageEvent): 消息事件对象。
            user_id (str): 用户 ID。

        Returns:
            MessageEventResult: 封禁结果消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            ban_system = BanSystem(config, msg_template)
            yield ban_system.remove(event, "123456789")
            ```
        """
        try:
            self.remove_ban(user_id)
            self._config.save_config()
            logger.info(f"已解封用户 {user_id}。")
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BanSystem", "RemoveBan", user_id=user_id
                )
            )
        except Exception:
            logger.exception("移除封禁用户时发生错误。")
            raise

    def list(
        self,
        event: AstrMessageEvent,
    ) -> MessageEventResult:
        """列出封禁用户列表。

        Args:
            event (AstrMessageEvent): 消息事件对象。

        Returns:
            MessageEventResult: 封禁结果消息事件结果

        Examples:
        ```python
            ban_system = BanSystem(config, msg_template)
            yield ban_system.list(event)
        ```
        """
        try:
            banlist = self.list_ban()
            if not banlist:
                return event.plain_result(
                    self._msg_template.get_msg_template("BanSystem", "BanlistEmpty")
                )
            banlist_lines = []
            for item in banlist:
                user_id = item["User"]
                reason = item.get("Reason") or "无"
                banlist_lines.append(
                    self._msg_template.get_msg_template(
                        "BanSystem",
                        "BanlistFormat",
                        user_id=user_id,
                        reason=reason,
                    )
                )
            banlist_str = "".join(banlist_lines)
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BanSystem", "ListBan", banlist=banlist_str
                )
            )
        except Exception:
            logger.exception("列出封禁用户列表时发生错误。")
            raise
