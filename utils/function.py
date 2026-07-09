from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)

from .api import ProtocolEndApi


async def check_self_role(event: AstrMessageEvent, group_id: int) -> tuple[bool, bool]:
    """检查机器人在给定群聊的身份。

    Args:
        event (AstrMessageEvent): 事件对象。
        group_id (int): 要检查的群聊 ID。

    Returns:
        tuple[bool, bool]: 是否是管理员，是否是群主。

    Raises:
        AssertionError: 如果事件对象来自非 aiocqhttp 平台。
    """
    assert isinstance(event, AiocqhttpMessageEvent)
    member_info = await ProtocolEndApi.get_group_member_info(
        event, group_id, int(event.get_self_id())
    )
    match member_info["role"]:
        case "member":
            return False, False
        case "admin":
            return True, False
        case "owner":
            return True, True
        case _:
            logger.warning(
                f"检测到未知的群成员角色: {member_info['role']}，这似乎不是 Onebot 11 的标准返回值。请检查插件是否兼容当前 AstrBot / NapCat 版本。"
            )
            return False, False
