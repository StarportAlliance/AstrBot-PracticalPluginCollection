from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult

from ...utils.api import ProtocolEndApi
from ...utils.message import MessageTemplate


class SendLike:
    """赞我模块。"""

    _msg_template: MessageTemplate

    _module_config: dict

    def __init__(self, msg_template: MessageTemplate, module_config: dict) -> None:
        self._msg_template = msg_template
        self._module_config = module_config

    async def like(
        self, event: AstrMessageEvent, times: int = 10
    ) -> MessageEventResult:
        """赞我！

        Args:
            event (AstrMessageEvent): 消息事件对象。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield like(event)
            ```
        """
        try:
            if times > 20 or times < 1:
                raise ValueError("点赞次数须在 1 到 20 之间。")
            await ProtocolEndApi.send_like(event, int(event.get_sender_id()), times)
            return event.plain_result(
                self._msg_template.get_msg_template("SendLike", "SendSuccess")
            )
        except ValueError:
            logger.info(
                f"用户 {event.get_sender_id()} 请求的点赞次数 {times} 无效，拒绝点赞请求。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("SendLike", "InvalidTimes")
            )
        except Exception:
            logger.exception("点赞用户时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )
