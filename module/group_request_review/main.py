import math
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import cast

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)

from ...core import BanSystem
from ...utils import check_self_role, event_filter
from ...utils.api import ProtocolEndApi
from ...utils.message import MessageTemplate
from .log import GroupRequestLog


class GroupRequestReview(GroupRequestLog):
    """加群请求审核模块。"""

    _message_template: MessageTemplate
    """消息模板。"""
    _module_config: dict
    """模块配置。"""
    _ban_system: BanSystem
    """封禁系统。"""

    @classmethod
    async def initialize(
        cls,
        plugin_data_path: Path,
        message_template: MessageTemplate,
        module_config: dict,
        ban_system: BanSystem,
    ):
        """初始化加群请求审核模块。

        Args:
            plugin_data_path (Path): 插件数据路径。
            message_template (MessageTemplate): 消息模板类实例。
            module_config (dict): 模块配置。
            ban_system (BanSystem): 封禁系统实例。

        Returns:
            GroupRequestReview: 模块实例。
        """
        self = await super().init(plugin_data_path)
        self._message_template = message_template
        self._module_config = module_config
        self._ban_system = ban_system
        return self

    async def handle_request_review(
        self,
        event: AstrMessageEvent,
    ):
        """处理加群请求。"""
        # 基础事件筛选
        if not self._module_config["Enable"]:
            return
        if not event_filter(event, "request", "group", "add"):
            return

        # 解析事件数据
        raw_message = cast(dict, event.message_obj.raw_message)
        group_id = str(raw_message["group_id"])
        user_id = str(raw_message["user_id"])
        raw_comment = str(raw_message["comment"])
        if "\n答案：" in raw_comment:
            input_answer = raw_comment.split("\n答案：", 1)[1]
        else:
            input_answer = raw_comment
            logger.warning(
                f"未能判断用户 {user_id} 加群实际输入答案，将使用原始内容作为输入：`{raw_comment}`。"
            )
        request_flag = str(raw_message["flag"])
        logger.info(
            f"收到用户 {user_id} 来自群 {group_id} 的加群请求，答案：`{input_answer}`。"
        )

        # 加载审核策略
        review_strategies = cast(list[dict], self._module_config["ReviewStrategy"])
        group_config = None
        for cfg in review_strategies:
            if cfg["__template_key"] == "Dedicated" and cfg["TargetGroup"] == group_id:
                group_config = cfg
                break
        if group_config is None:
            for cfg in review_strategies:
                if cfg["__template_key"] == "Common":
                    group_config = cfg
                    break
        if group_config is None:
            logger.warning(
                f"未能为群 {group_id} 找到可用的审核策略，请检查你的插件配置是否已正确配置对应策略。此次加群请求将被忽略。"
            )
            return

        # 主要判断逻辑部分
        if group_config["UseBanlist"]:
            if self._ban_system.check_user_is_banned(user_id):
                logger.info(f"用户 {user_id} 已被封禁，将拒绝其加群请求。")
                await self._handle_request(
                    event,
                    request_flag,
                    False,
                    self._message_template.get_msg_template(
                        "GroupRequestReview", "RejectByBanned"
                    ),
                )
                return
        time_limit = cast(dict, group_config["TimeLimit"])
        if time_limit["Enable"]:
            statistical_time = int(time_limit["StatisticalTime"])
            total_attempt = int(time_limit["TotalAttempt"])
            cutoff_time = (
                datetime.now() - timedelta(minutes=statistical_time)
            ).strftime("%Y-%m-%d %H:%M:%S")
            recent_requests = await self.get_requests(user_id, cutoff_time)
            if len(recent_requests) >= total_attempt:
                logger.info(
                    f"用户 {user_id} 在 {statistical_time} 分钟内请求 {len(recent_requests)} 次，超过上限 {total_attempt}，将拒绝其加群请求。"
                )
                earliest_request_time = min(
                    datetime.strptime(req["request_time"], "%Y-%m-%d %H:%M:%S")
                    for req in recent_requests
                )
                remaining_delta = (
                    earliest_request_time
                    + timedelta(minutes=statistical_time)
                    - datetime.now()
                )
                remaining_time = math.ceil(remaining_delta.total_seconds() / 60)
                await self._handle_request(
                    event,
                    request_flag,
                    False,
                    self._message_template.get_msg_template(
                        "GroupRequestReview",
                        "RejectByRateLimit",
                        remaining_time=str(remaining_time),
                    ),
                )
                return
            # 即使没有通过下面的其他限制也需要计入请求次数
            await self.add_request(user_id)
        level_limit = cast(dict, group_config["LevelLimit"])
        if level_limit["MinLevel"] > 0:
            member_info = await ProtocolEndApi.get_stranger_info(
                event, int(user_id), True
            )
            if member_info["isHideQQLevel"]:
                if not level_limit["SkipInvalidLevel"]:
                    logger.info(f"用户 {user_id} 隐藏了 QQ 等级，将拒绝其加群请求。")
                    await self._handle_request(
                        event,
                        request_flag,
                        False,
                        self._message_template.get_msg_template(
                            "GroupRequestReview", "RejectByInvalidLevel"
                        ),
                    )
                    return
                logger.debug(
                    f"用户 {user_id} 隐藏了 QQ 等级，但插件配置中启用了跳过无效等级，将绕过等级限制。"
                )
            elif member_info["qqLevel"] < level_limit["MinLevel"]:
                logger.info(
                    f"用户 {user_id} 等级 {member_info['qqLevel']} 低于要求的最小等级 {level_limit['MinLevel']}，将拒绝其加群请求。"
                )
                await self._handle_request(
                    event,
                    request_flag,
                    False,
                    self._message_template.get_msg_template(
                        "GroupRequestReview",
                        "RejectByLevelLimit",
                        required_level=level_limit["MinLevel"],
                    ),
                )
                return
        match = re.search(group_config["Regex"], input_answer)
        if not match:
            logger.info(f"用户 {user_id} 答案中未匹配到关键词，将拒绝其加群请求。")
            await self._handle_request(
                event,
                request_flag,
                False,
                self._message_template.get_msg_template(
                    "GroupRequestReview", "RejectByRegex"
                ),
            )
            return

        # 检查全部通过，同意加群请求
        logger.info(
            f"用户 {user_id} 答案中匹配了关键词 `{match.group()}`，将同意其加入群 {group_id}。"
        )
        await self._handle_request(event, request_flag, True)
        return

    @staticmethod
    async def _handle_request(
        event: AstrMessageEvent, request_flag: str, approve: bool, reason: str = ""
    ):
        """处理加群请求。

        Args:
            event (AstrMessageEvent): 事件对象。
            request_flag (str): 加群请求 flag。
            approve (bool): 是否同意加群请求。
            reason (str, optional): 拒绝原因，仅在拒绝加群请求时有效。若不传入或传入空字符串则表示无理由拒绝。
        """
        is_admin, _ = await check_self_role(event, int(event.get_group_id()))
        if not is_admin:
            raise PermissionError("机器人不是当前群聊管理员，无法处理加群请求。")

        assert isinstance(event, AiocqhttpMessageEvent)
        await ProtocolEndApi.set_group_add_request(
            event, request_flag, "add", approve, reason
        )
