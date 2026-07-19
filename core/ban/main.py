from typing import cast

from astrbot.api import AstrBotConfig, logger


class BanSystemCore:
    """封禁系统核心功能类。"""

    _config: AstrBotConfig
    """插件配置。"""
    _ban_list: list[dict]
    """封禁用户列表。"""

    def __init__(self, config: AstrBotConfig):
        """初始化封禁系统。

        Args:
            config (AstrBotConfig): 插件配置。
        """
        self._config = config
        self._ban_list = cast(
            list[dict], self._config["CoreConfig"]["BanSystem"]["Banlist"]
        )
        logger.debug("封禁系统核心功能初始化完成。")

    def add_ban(self, user_id: str, reason: str):
        """添加封禁用户。

        Args:
            user_id (str): 用户 ID。
            reason (str): 封禁原因。

        Raises:
            ValueError: 如果用户已被封禁。
        """
        if any(item["User"] == user_id for item in self._ban_list):
            raise ValueError(f"用户 {user_id} 已被封禁，无法重复添加。")
        self._ban_list.append(
            {"__template_key": "SingleBan", "User": user_id, "Reason": reason}
        )
        self._config.save_config()

    def remove_ban(self, user_id: str):
        """移除封禁用户。

        Args:
            user_id (str): 用户 ID。

        Raises:
            ValueError: 如果用户未被封禁。
        """
        if not any(item["User"] == user_id for item in self._ban_list):
            raise ValueError(f"用户 {user_id} 未被封禁，无法移除。")
        self._ban_list = [item for item in self._ban_list if item["User"] != user_id]
        self._config.save_config()

    def list_ban(self) -> list[dict]:
        """获取封禁用户列表。

        Returns:
            list[dict]: 封禁用户列表。
        """
        return self._ban_list

    def check_user_is_banned(self, user_id: str) -> bool:
        """检查用户是否被封禁。

        Args:
            user_id (str): 用户 ID。

        Returns:
            bool: 是否被封禁。
        """
        return any(item["User"] == user_id for item in self._ban_list)
