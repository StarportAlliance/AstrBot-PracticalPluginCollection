from typing import cast

from astrbot.api import logger


class MessageTemplate:
    """消息模板类。"""

    _template: dict[str, dict[str, str]]
    """消息模板配置。"""

    def __init__(self, template_config: dict):
        """初始化消息模板类。

        Args:
            template_config (dict): 消息模板配置。
        """
        self._template = template_config

    def get_msg_template(
        self, template_module: str, template_name: str, **kwargs: str
    ) -> str:
        """获取消息模板。

        Args:
            template_module (str): 消息模板模块，即消息模板是在哪个模块定义的。
            template_name (str): 消息模板名称。
            **kwargs (str): 可选，如果消息模板有占位符，可以传递参数，方法将自动尝试替换。

        Returns:
            str: 消息模板内容。

        Raises:
            KeyError: 如果消息模板不存在。
        """
        try:
            msg_template = cast(str, self._template[template_module][template_name])
            for key, value in kwargs.items():
                msg_template = msg_template.replace(f"{{{key}}}", value)
            return msg_template
        except KeyError:
            # 有意添加日志以便更清晰的追踪问题来源
            logger.error(
                f"获取消息模板时发生错误，消息模板 {template_module}.{template_name} 不存在。"
            )
            raise
