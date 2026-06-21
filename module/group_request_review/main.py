"""加群请求自动审核模块，提供了基于正则表达式的加群自动处理功能，能够通过正则判断入群答案从而自动同意/拒绝请求，支持等级/速率限制等筛选条件。"""

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent
from typing import cast
from ..utils import (
    event_filter,
    BanSystem,
    ProtocolEndApi,
    check_self_role,
)
import re
from datetime import datetime, timedelta


async def handle_request_review(
    event: AstrMessageEvent,
    module_config: dict,
    ban_system: BanSystem,
    group_request_log,
):
    """处理加群请求。"""
    # 基础事件筛选
    if not module_config["Enable"]:
        return
    if not event_filter(event, "request", "group", "add"):
        return

    # 解析事件数据
    raw_message = cast(dict, event.message_obj.raw_message)
    group_id = str(raw_message["group_id"])
    user_id = str(raw_message["user_id"])
    input_answer = str(raw_message["comment"])
    request_flag = str(raw_message["flag"])
    logger.info(
        f"收到用户 {user_id} 来自群 {group_id} 的加群请求，答案：{input_answer}。"
    )

    # 加载审核策略
    review_strategies = cast(list[dict], module_config["ReviewStrategy"])
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
    message_template = cast(dict, module_config["MessageTemplate"])
    if group_config["UseBanlist"]:
        if await ban_system.check_user_is_banned(user_id):
            logger.info(f"用户 {user_id} 已被封禁，将拒绝其加群请求。")
            await _handle_request(
                event, request_flag, False, message_template["RejectByBanned"]
            )
            return
    time_limit = cast(dict, group_config["TimeLimit"])
    if time_limit["Enable"]:
        statistical_time = time_limit["StatisticalTime"]
        total_attempt = time_limit["TotalAttempt"]
        cutoff_time = (datetime.now() - timedelta(minutes=statistical_time)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        recent_requests = await group_request_log.get_requests_since(
            user_id, cutoff_time
        )
        if len(recent_requests) >= total_attempt:
            logger.info(
                f"用户 {user_id} 在 {statistical_time} 分钟内请求 {len(recent_requests)} 次，超过上限 {total_attempt}，将拒绝其加群请求。"
            )
            await _handle_request(
                event, request_flag, False, message_template["RejectByRateLimit"]
            )
            return
        await group_request_log.add_request(user_id)
    level_limit = cast(dict, group_config["LevelLimit"])
    if level_limit["MinLevel"] > 0:
        member_info = await ProtocolEndApi.get_stranger_info(event, user_id, True)
        if member_info["isHideQQLevel"]:
            if not level_limit["SkipInvalidLevel"]:
                logger.info(f"用户 {user_id} 隐藏了 QQ 等级，将拒绝其加群请求。")
                await _handle_request(
                    event, request_flag, False, message_template["RejectByInvalidLevel"]
                )
                return
            logger.debug(
                f"用户 {user_id} 隐藏了 QQ 等级，但插件配置中启用了跳过无效等级，将绕过等级限制。"
            )
        elif member_info["qqLevel"] < level_limit["MinLevel"]:
            logger.info(
                f"用户 {user_id} 等级 {member_info['qqLevel']} 低于要求的最小等级 {level_limit['MinLevel']}，将拒绝其加群请求。"
            )
            await _handle_request(
                event, request_flag, False, message_template["RejectByLevelLimit"]
            )
            return
    match = re.search(group_config["Regex"], input_answer)
    if not match:
        logger.info(f"用户 {user_id} 答案中未匹配到关键词，将拒绝其加群请求。")
        await _handle_request(
            event, request_flag, False, message_template["RejectByRegex"]
        )
        return

    # 检查全部通过，同意加群请求
    logger.info(
        f"用户 {user_id} 答案中匹配了关键词 {match.group()}，将同意其加入群 {group_id}。"
    )
    await _handle_request(event, request_flag, True)
    return


async def _handle_request(
    event: AstrMessageEvent, request_flag: str, approve: bool, reason: str = ""
) -> bool:
    """处理加群请求。

    Args:
        event (AstrMessageEvent): 事件对象。
        request_flag (str): 加群请求 flag。
        approve (bool): 是否同意加群请求。
        reason (str, optional): 拒绝原因，仅在拒绝加群请求时有效。若不传入或传入空字符串则表示无理由拒绝。

    Returns:
        bool: 如果拒绝成功则返回 True，否则返回 False。
    """
    try:
        if not check_self_role(event, event.get_group_id())[0]:
            logger.error(
                "机器人身份校验失败。机器人不是当前群聊管理员，无法处理加群请求。"
            )
            return False
        from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
            AiocqhttpMessageEvent,
        )

        assert isinstance(event, AiocqhttpMessageEvent)
        await ProtocolEndApi.set_group_add_request(
            event, request_flag, "add", approve, reason
        )
        return True
    except AssertionError:
        logger.exception(
            "加群请求事件对象类型校验失败。这可能意味着插件源代码遭到了不合理的改动，或不兼容当前的 AstrBot 版本。",
        )
        return False
    except Exception:
        logger.exception("处理加群请求时发生意外错误。")
        return False
