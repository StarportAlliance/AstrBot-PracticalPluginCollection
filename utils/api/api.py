from typing import Any, Literal, cast

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)


class ProtocolEndApi:
    """调用 NapCat（协议端）API。"""

    @staticmethod
    async def set_group_add_request(
        event: AstrMessageEvent | AiocqhttpMessageEvent,
        request_flag: str,
        sub_type: Literal["invite", "add"],
        approve: bool,
        reason: str = "",
    ):
        """## 处理加群请求

        同意或拒绝加群请求或邀请。

        Args:
            event (AiocqhttpMessageEvent): 事件对象。
            request_flag (str): 加群请求 flag。
            sub_type (Literal["invite", "add"]): 加群请求类型，`"invite"` 表示邀请登录号入群，`"add"` 表示他人加群请求。
            approve (bool): 是否同意加群请求。
            reason (str, optional): 拒绝原因，仅在拒绝加群请求时有效。若不传入或传入空字符串则表示无理由拒绝。

        Raises:
            AssertionError: 如果事件对象来自非 aiocqhttp 平台。
        """
        assert isinstance(event, AiocqhttpMessageEvent)
        client = event.bot
        payloads: dict[str, Any] = {
            "flag": request_flag,
            "sub_type": sub_type,
            "approve": approve,
            "reason": reason,
            "self_id": int(event.get_self_id()),
        }
        await client.api.set_group_add_request(**payloads)
        logger.debug(
            f"请求了协议端 API /set_group_add_request，请求参数：`{payloads}`。"
        )

    @staticmethod
    async def get_group_member_info(
        event: AstrMessageEvent | AiocqhttpMessageEvent,
        group_id: int,
        user_id: int,
        no_cache: bool = False,
    ) -> dict[str, int | str | bool]:
        """## 获取群成员信息

        获取群聊中指定成员的信息。

        Args:
            event (AiocqhttpMessageEvent): 事件对象。
            group_id (int): 群聊 ID。
            user_id (int): 要获取信息的用户 ID。
            no_cache (bool, optional): 是否绕过缓存获取信息。通过缓存获取信息更快，但可能存在更新延迟。默认优先使用缓存数据即不绕过缓存。

        Returns:
            dict[str, int | str | bool]: 给定的群成员的信息。

        Raises:
            AssertionError: 如果事件对象来自非 aiocqhttp 平台。
        """
        assert isinstance(event, AiocqhttpMessageEvent)
        client = event.bot
        payloads: dict[str, Any] = {
            "group_id": group_id,
            "user_id": user_id,
            "no_cache": no_cache,
            "self_id": int(event.get_self_id()),
        }
        member_info = await client.api.get_group_member_info(**payloads)
        logger.debug(
            f"请求了协议端 API /get_group_member_info，请求参数：`{payloads}`，返回结果：`{member_info}`。"
        )
        return cast(dict[str, int | str | bool], member_info)

    @staticmethod
    async def get_stranger_info(
        event: AstrMessageEvent | AiocqhttpMessageEvent,
        user_id: int,
        no_cache: bool = False,
    ) -> dict[str, int | str | bool]:
        """## 获取陌生人信息

        获取指定非好友用户的信息。

        Args:
            event (AstrMessageEvent | AiocqhttpMessageEvent): 事件对象。
            user_id (int): 要获取信息的用户 ID。
            no_cache (bool, optional): 是否绕过缓存获取信息。通过缓存获取信息更快，但可能存在更新延迟。默认优先使用缓存数据即不绕过缓存。

        Returns:
            dict[str, int | str | bool]: 给定的陌生人用户的信息。

        Raises:
            AssertionError: 如果事件对象来自非 aiocqhttp 平台。
        """
        assert isinstance(event, AiocqhttpMessageEvent)
        client = event.bot
        payloads: dict[str, Any] = {
            "user_id": user_id,
            "no_cache": no_cache,
            "self_id": int(event.get_self_id()),
        }
        stranger_info = await client.api.get_stranger_info(**payloads)
        logger.debug(
            f"请求了协议端 API /get_stranger_info，请求参数：`{payloads}`，返回结果：`{stranger_info}`。"
        )
        return cast(dict[str, int | str | bool], stranger_info)
