from .db import BanSystemDataBase
from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger


class BanSystem(BanSystemDataBase):
    """封禁系统。"""

    async def add(
        self, event: AstrMessageEvent, user_id: int, reason: str = "", duration: int = 0
    ):
        """封禁给定用户。

        Args:
            event (AstrMessageEvent): 消息事件对象。
            user_id (int): 要封禁的用户ID。
            reason (str, optional): 封禁原因。 Defaults to "".
            duration (int, optional): 封禁时长，单位为分钟，默认为 `0` 即永久封禁。
        """
        try:
            await self.add_ban(
                user_id, event.get_group_id(), event.get_sender_id(), reason, duration
            )
            yield event.plain_result(f"封禁 {user_id} 成功。")
            return
        except Exception:
            logger.exception(f"封禁用户 {user_id} 时发生错误。")
            yield event.plain_result("封禁用户时发生意外错误，请重试。")
            return

    async def remove(self, event: AstrMessageEvent, user_id: int):
        """解封给定用户。

        Args:
            event (AstrMessageEvent): 消息事件对象。
            user_id (int): 要解封的用户ID。
        """
        try:
            await self.del_ban(user_id, event.get_sender_id())
            yield event.plain_result(f"解封 {user_id} 成功。")
            return
        except Exception:
            logger.exception(f"解封用户 {user_id} 时发生错误。")
            yield event.plain_result("解封用户时发生意外错误，请重试。")
            return
