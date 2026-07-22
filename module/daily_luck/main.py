from pathlib import Path
from random import choice

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult

from ...utils.message.msg import MessageTemplate
from .db import DailyLuckDataBase


class DailyLuck:
    """今日人品模块。"""

    _msg_template: MessageTemplate
    """消息模板。"""
    _module_msg_template: dict
    """模块消息模板。"""
    _plugin_data_path: Path
    """插件数据目录。"""
    _db: DailyLuckDataBase
    """今日人品数据库。"""

    @classmethod
    async def init(
        cls,
        msg_template: MessageTemplate,
        module_msg_template: dict,
        plugin_data_path: Path,
    ):
        """初始化今日人品模块。

        Args:
            msg_template (MessageTemplate): 模块消息模板。
            module_msg_template (dict): 模块消息模板。
            plugin_data_path (Path): 插件数据目录。
        """
        ins = cls()
        ins._msg_template = msg_template
        ins._module_msg_template = module_msg_template
        ins._plugin_data_path = plugin_data_path
        ins._db = await DailyLuckDataBase.init(plugin_data_path)
        logger.debug("今日人品模块初始化完成。")
        return ins

    async def extract(self, event: AstrMessageEvent) -> MessageEventResult:
        """获取今日幸运值。

        Args:
            event (AstrMessageEvent): 消息事件对象。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            daily_luck = DailyLuck(msg_template, plugin_data_path)
            yield await daily_luck.extract(event)
            ```
        """
        try:
            user_id = event.get_sender_id()
            user_name = event.get_sender_name()
            luck = await self._db.try_get_luck(user_id)
            logger.debug(f"用户 {user_id} 的今日人幸运值为 {luck}。")
            template_configs = self._module_msg_template["templates"]
            fixed_templates = [
                config["Message"]
                for config in template_configs
                if config["__template_key"] == "FixedValue" and config["Value"] == luck
            ]
            range_templates = [
                config["Message"]
                for config in template_configs
                if config["__template_key"] == "SpecifiedRange"
                and config["RangeStart"] <= luck <= config["RangeEnd"]
            ]
            if not fixed_templates and not range_templates:
                raise ValueError(f"未找到幸运值 {luck} 可用的消息模板。")
            message = choice(fixed_templates or range_templates)
            message = (
                message.replace("{user_id}", user_id)
                .replace("{user_name}", user_name)
                .replace("{value}", str(luck))
            )
            return event.plain_result(message)
        except ValueError:
            logger.error(
                "幸运值查询结果文案消息模板未被添加或未被全覆盖，请在配置中添加或补全相应模板。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "General",
                    "TemplateNotFound",
                    module_name="daily_luck",
                    module_template_name="幸运值查询结果文案 (Key: template)",
                )
            )
        except Exception:
            logger.exception("获取今日幸运值时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )
