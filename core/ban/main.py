from typing import cast

from astrbot.api import logger


class BanSystemCore:
    """封禁系统核心功能类。"""

    _ban_system_config: dict
    """封禁系统配置。"""
    _ban_list: list[dict]
    """封禁用户列表。"""

    def __init__(self, ban_system_config: dict):
        """初始化封禁系统。

        Args:
            ban_system_config (dict): 封禁系统配置。
        """
        self._ban_system_config = ban_system_config
        self._ban_list = cast(list[dict], self._ban_system_config["Banlist"])
        logger.debug("封禁系统核心功能初始化完成。")

    def add_ban(self, user_id: str, reason: str) -> bool:
        """添加封禁用户。

        Args:
            user_id (str): 用户 ID。
            reason (str): 封禁原因。

        Returns:
            bool: 是否请求保存配置。当此值为 True 时，调用处应当调用 `config.save_config` 方法保存配置以使封禁列表真正被写入。
        """
        if any(item["User"] == user_id for item in self._ban_list):
            logger.debug(f"用户 {user_id} 已被封禁，无需重复添加。")
            return False
        self._ban_list.append(
            {"__template_key": "SingleBan", "User": user_id, "Reason": reason}
        )
        logger.debug(f"添加了新的封禁用户 {user_id}。")
        return True

    def remove_ban(self, user_id: str) -> bool:
        """移除封禁用户。

        Args:
            user_id (str): 用户 ID。

        Returns:
            bool: 是否请求保存配置。当此值为 True 时，调用处应当调用 `config.save_config` 方法保存配置以使封禁列表真正被写入。
        """
        self._ban_list = [item for item in self._ban_list if item["User"] != user_id]
        logger.debug(f"移除了封禁用户 {user_id}。")
        return True

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
