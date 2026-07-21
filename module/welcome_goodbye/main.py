from typing import Literal, cast

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult
from astrbot.api.message_components import At, BaseMessageComponent, Plain

from ...utils.api import ProtocolEndApi
from ...utils.filter import event_filter


class WelcomeGoodbye:
    """进退群提醒模块。"""

    _module_msg_template: dict
    """模块消息模板。"""

    def __init__(self, module_msg_template: dict):
        """初始化进退群提醒模块。

        Args:
            module_msg_template (dict): 模块消息模板。
        """
        self._module_msg_template = module_msg_template
        logger.debug("进退群提醒模块初始化完成。")

    async def handle_event(self, event: AstrMessageEvent) -> MessageEventResult | None:
        """处理进退群事件。

        Args:
            event (AstrMessageEvent): 消息事件对象。

        Returns:
            MessageEventResult | None: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            welcome_goodbye = WelcomeGoodbye(msg_template)
            yield await welcome_goodbye.handle_event(event)
            ```
        """
        try:
            if not event_filter(event, "notice", "group_increase") and not event_filter(
                event, "notice", "group_decrease"
            ):
                return None

            raw_message = cast(dict, event.message_obj.raw_message)
            notice_type = cast(
                Literal["group_increase", "group_decrease"], raw_message["notice_type"]
            )
            sub_type = str(raw_message["sub_type"])
            # 理论上触发 group_increase / group_decrease 事件只能是群聊，这里不进一步校验群号
            group_id = str(event.get_group_id())
            user_id = str(raw_message["user_id"])

            # 如果是机器人被踢则不处理
            if notice_type == "group_decrease" and sub_type == "kick_me":
                return None

            if notice_type == "group_increase":
                template_configs = cast(
                    list[dict], self._module_msg_template["WelcomeMsg"]
                )
                message_key = "Message"
            elif sub_type in {"leave", "kick"}:
                template_configs = cast(
                    list[dict], self._module_msg_template["GoodbyeMsg"]
                )
                message_key = "LeaveMessage" if sub_type == "leave" else "KickMessage"
            else:
                return None

            group_config = None
            for config in template_configs:
                if (
                    config["__template_key"] == "Dedicated"
                    and str(config["TargetGroup"]) == group_id
                ):
                    group_config = config
                    break
            if group_config is None:
                for config in template_configs:
                    if config["__template_key"] == "Common":
                        group_config = config
                        break
            if group_config is None:
                logger.warning(
                    f"未能为群 {group_id} 找到可用的进退群提醒消息配置，此次事件将被忽略。"
                )
                return None

            message = str(group_config[message_key])

            # 消息事件只包含用户 ID，需要调用协议端 API 获取名称
            user_info = await ProtocolEndApi.get_stranger_info(event, int(user_id))
            user_name = str(user_info["nickname"])
            message = message.replace("{user_id}", user_id).replace(
                "{user_name}", user_name
            )
            if notice_type == "group_decrease" and sub_type == "kick":
                operator_id = str(raw_message["operator_id"])
                operator_info = await ProtocolEndApi.get_group_member_info(
                    event, int(group_id), int(operator_id)
                )
                operator_name = str(operator_info["nickname"])
                message = message.replace("{operator_id}", operator_id).replace(
                    "{operator_name}", operator_name
                )

            # 构造消息链
            chain: list[BaseMessageComponent] = []
            segments = message.split("{at_user}")
            for i, segment in enumerate(segments):
                if segment:
                    # 不知道是 astrbot 还是 aiocqhttp 的弱智行为纯文本消息会 strip()，
                    # 这里需要加零宽空格特殊处理一下
                    if segment[0].isspace():
                        segment = "\u200b" + segment
                    if segment[-1].isspace():
                        segment = segment + "\u200b"
                    chain.append(Plain(segment))
                if i < len(segments) - 1:
                    chain.append(At(qq=user_id))

            return event.chain_result(chain)

        except Exception:
            logger.exception("处理进退群事件时发生错误。")
            return None
